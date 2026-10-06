# coding: utf-8

import hashlib
import multiprocessing
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.process import BrokenProcessPool, ProcessPoolExecutor
from copy import deepcopy
from typing import List, Tuple

from supervisely import FrameCollection, VideoAnnotation, VideoTagCollection, logger
from supervisely.api.video.video_api import VideoInfo

import src.globals as g
from src.compute.custom_code import runner
from src.compute.dtl_utils.item_descriptor import VideoDescriptor
from src.compute.Layer import Layer
from src.compute.layers.processing.SplitVideoByDurationLayer import (
    get_ann_tags,
    get_frame_range_tags,
    make_new_video_info,
    process_splits,
)
from src.exceptions import GraphError


AUTO_MAX_WORKERS = 8


def clip_annotation(ann: VideoAnnotation, start: int, end: int, frames_count: int) -> VideoAnnotation:
    """Annotation of frames start..end, re-indexed so that `start` becomes frame 0."""
    frames = []
    for frame in ann.frames:
        if start <= frame.index <= end and frame.index - start < frames_count:
            index = frame.index - start
            figures = [figure.clone(frame_index=index) for figure in frame.figures]
            frames.append(frame.clone(index=index, figures=figures))
    video_tags, frame_range_tags = get_ann_tags(ann)
    tags = deepcopy(video_tags)
    tags.extend(get_frame_range_tags(frame_range_tags, [start, start + frames_count]))
    return ann.clone(
        frames_count=frames_count,
        frames=FrameCollection(frames),
        tags=VideoTagCollection(tags),
    )


class CustomCodeLayer(Layer):
    """Runs process(video_path, video_info, ann, params) from a Team Files script on every video
    and keeps the frame ranges it returns: one clip per range, [] drops the video, one range over
    the whole video passes it through unchanged. Videos run in parallel in a process pool."""

    action = "custom_code"
    _with_pools = set()

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["script_path"],
                "properties": {
                    "script_path": {"type": "string", "minLength": 1},
                    "params": {"type": "object"},
                    "workers": {"type": "integer", "minimum": 0},
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)
        self._pool = None
        self._script_local_path = None
        self._clips_dir = None
        self._stats = {"videos": 0, "clips": 0, "passed": 0, "dropped": 0, "errors": 0}

    def validate(self):
        super().validate()
        if not g.CUSTOM_CODE_ENABLED:
            raise GraphError(
                "The Custom Code node is turned off in this app. It runs only in an app whose "
                "image sets ML_PIPELINES_CUSTOM_CODE=1",
                extra={},
            )
        if self.net is not None and self.net.modality != "videos":
            raise GraphError("The Custom Code node works on videos only", extra={})

    def modifies_data(self):
        return True

    def requires_item(self):
        return True

    def workers(self) -> int:
        workers = self.settings.get("workers", 0)
        if workers <= 0:
            # Each worker holds its own interpreter, SDK and script (about 350 MB before the
            # script's own imports), and video decoding already uses several cores per video.
            workers = min(os.cpu_count() or 1, AUTO_MAX_WORKERS)
        return workers

    def video_batch_size(self) -> int:
        return self.workers()

    def _create_pool(self):
        # spawn: the app is multi-threaded, and forking it could deadlock the workers.
        self._pool = ProcessPoolExecutor(
            max_workers=self.workers(), mp_context=multiprocessing.get_context("spawn")
        )
        CustomCodeLayer._with_pools.add(self)

    def _shutdown_pool(self):
        if self._pool is not None:
            self._pool.shutdown(wait=False, cancel_futures=True)
            self._pool = None
        CustomCodeLayer._with_pools.discard(self)

    def preprocess(self):
        # A run that failed or was stopped never reached postprocess(): free its workers.
        for layer in list(CustomCodeLayer._with_pools):
            if layer.net is not self.net:
                layer._shutdown_pool()
        if self.net.preview_mode:
            return
        script_path = self.settings["script_path"]
        if not g.api.file.exists(g.TEAM_ID, script_path):
            raise GraphError(f"Custom Code script not found in Team Files: {script_path}", extra={})
        work_dir = tempfile.mkdtemp(prefix="custom_code_", dir=g.DATA_DIR)
        self._script_local_path = os.path.join(work_dir, os.path.basename(script_path))
        # Not under RESULTS_DIR: every folder there is archived and uploaded as a result project.
        self._clips_dir = os.path.join(work_dir, "clips")
        g.api.file.download(g.TEAM_ID, script_path, self._script_local_path)
        with open(self._script_local_path, "rb") as f:
            code_hash = hashlib.sha256(f.read()).hexdigest()
        logger.info(
            f"Custom Code: running {script_path} (sha256 {code_hash}) with {self.workers()} workers",
            extra={"script_path": script_path, "sha256": code_hash, "workers": self.workers()},
        )
        self._create_pool()
        try:
            self._pool.submit(runner.check_script, self._script_local_path).result()
        except Exception as e:
            self._shutdown_pool()
            raise GraphError(f"Custom Code script {script_path} could not be loaded: {e}", extra={})

    def postprocess(self):
        self._shutdown_pool()
        if self._script_local_path is not None:
            logger.info(
                "Custom Code: {videos} videos, {clips} clips, {passed} passed unchanged, "
                "{dropped} dropped, {errors} failed".format(**self._stats),
                extra=dict(self._stats),
            )

    def _report_error(self, vid_desc: VideoDescriptor, error: Exception):
        self._stats["errors"] += 1
        g.disable_move = True
        logger.warning(
            f"Custom Code: video '{vid_desc.info.item_info.name}' skipped: "
            f"{type(error).__name__}: {error}",
            exc_info=error,
            extra={"video_id": vid_desc.info.item_info.id},
        )

    def process_batch(self, data_els: List[Tuple[VideoDescriptor, VideoAnnotation]]):
        if self.net.preview_mode:
            yield data_els
            return
        if len(data_els) == 0:
            return
        if self._pool is None:
            self._create_pool()

        def download(data_el):
            try:
                return data_el[0].item_data
            except Exception as e:
                return e

        with ThreadPoolExecutor(max_workers=min(len(data_els), 8)) as executor:
            video_paths = list(executor.map(download, data_els))

        meta_json = self.output_meta.to_json()
        params = self.settings.get("params", {})
        ffmpeg_threads = max(1, (os.cpu_count() or 1) // self.workers())
        jobs = {}
        results = {}
        for idx, ((vid_desc, ann), video_path) in enumerate(zip(data_els, video_paths)):
            if isinstance(video_path, Exception):
                results[idx] = video_path
            elif g.pipeline_running:
                jobs[idx] = (
                    self._script_local_path,
                    video_path,
                    vid_desc.info.item_info._asdict(),
                    ann.to_json(),
                    meta_json,
                    params,
                    self._clips_dir,
                    ffmpeg_threads,
                )
        results.update(self._run_jobs(jobs))

        outputs = []
        for idx, (vid_desc, ann) in enumerate(data_els):
            if idx not in results:
                continue
            self._stats["videos"] += 1
            result = results[idx]
            if isinstance(result, Exception):
                self._report_error(vid_desc, result)
                continue

            if len(result["ranges"]) == 0:
                self._stats["dropped"] += 1
            elif len(result["clips"]) == 0:
                self._stats["passed"] += 1
                outputs.append((vid_desc, ann))
            else:
                try:
                    outputs.extend(self._make_clips(vid_desc, ann, result["clips"]))
                except Exception as e:
                    self._report_error(vid_desc, e)
        if len(outputs) > 0:
            yield outputs

    def _run_jobs(self, jobs: dict) -> dict:
        """Run runner.run_video for every job: {index: result or the exception it raised}."""
        futures = {idx: self._pool.submit(runner.run_video, *args) for idx, args in jobs.items()}
        results, crashed = {}, []
        for idx, future in futures.items():
            try:
                results[idx] = future.result()
            except BrokenProcessPool:
                crashed.append(idx)
            except Exception as e:
                results[idx] = e
        if len(crashed) > 0:
            # A worker process died (the script crashed the interpreter), and every video still
            # in the pool failed with it. Re-run those one at a time to find the one responsible.
            logger.warning(
                f"Custom Code: a worker process died. Re-running {len(crashed)} videos one at a time"
            )
            self._shutdown_pool()
            self._create_pool()
            for idx in crashed:
                try:
                    results[idx] = self._pool.submit(runner.run_video, *jobs[idx]).result()
                except BrokenProcessPool:
                    results[idx] = RuntimeError(
                        "the script ended its worker process "
                        "(a crash in native code, os._exit() or running out of memory)"
                    )
                    self._shutdown_pool()
                    self._create_pool()
                except Exception as e:
                    results[idx] = e
        return results

    def _make_clips(self, vid_desc: VideoDescriptor, ann: VideoAnnotation, clips: list):
        video_info: VideoInfo = vid_desc.info.item_info
        outputs = []
        for start, end, clip_path in clips:
            clip_name = os.path.basename(clip_path)
            clip_info = make_new_video_info(
                video_info._replace(file_meta=deepcopy(video_info.file_meta)), clip_name, clip_path
            )
            expected = end - start + 1
            if clip_info.frames_count != expected:
                logger.warning(
                    f"Custom Code: clip {clip_name} has {clip_info.frames_count} frames, "
                    f"expected {expected}. Its annotation is trimmed to the clip."
                )
            clip_ann = clip_annotation(ann, start, end, min(expected, clip_info.frames_count))
            outputs.append(process_splits(vid_desc, clip_path, clip_name, clip_ann, clip_info))
            self._stats["clips"] += 1
        return outputs

    def has_batch_processing(self):
        return True
