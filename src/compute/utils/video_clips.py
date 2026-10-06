# coding: utf-8
"""Cut clips with arbitrary frame ranges out of a video, with annotations re-indexed."""

import os
import shutil
import subprocess
from copy import deepcopy
from typing import List, NamedTuple, Optional, Sequence, Tuple

from supervisely import FrameCollection, VideoAnnotation, VideoTagCollection
from supervisely.api.video.video_api import VideoInfo
from supervisely.io.fs import get_file_name
from supervisely.sly_logger import logger
from supervisely.video.video import get_info as get_video_info

import src.globals as g
from src.compute.dtl_utils.item_descriptor import VideoDescriptor
from src.utils import LegacyProjectItem


class Clip(NamedTuple):
    path: str
    name: str
    info: VideoInfo
    ann: VideoAnnotation
    start: int  # first frame of the clip in the source video
    end: int  # last frame of the clip in the source video (inclusive)


def normalize_ranges(ranges: Sequence, frames_count: int) -> List[Tuple[int, int]]:
    """Validate inclusive (start, end) frame ranges against a video with `frames_count` frames."""
    result = []
    for frame_range in ranges:
        try:
            start, end = frame_range
            start, end = int(start), int(end)
        except (TypeError, ValueError):
            raise ValueError(
                f"Frame range {frame_range!r} must be a (start, end) pair of frame indexes."
            )
        if not 0 <= start <= end < frames_count:
            raise ValueError(
                f"Frame range ({start}, {end}) is outside the video's frames 0..{frames_count - 1}."
            )
        result.append((start, end))
    return result


def get_ann_tags(ann: VideoAnnotation) -> tuple:
    video_tags = []
    frame_range_tags = []
    for tag in ann.tags:
        if tag.frame_range is None:
            video_tags.append(tag)
        else:
            frame_range_tags.append(tag)
    return video_tags, frame_range_tags


def get_frame_range_tags(frame_range_tags, start: int, end: int) -> list:
    """Frame range tags that overlap frames start..end, cut to them and re-indexed from `start`."""
    result_tags = []
    for tag in frame_range_tags:
        tag_start = max(tag.frame_range[0], start)
        tag_end = min(tag.frame_range[1], end)
        if tag_start > tag_end:
            continue
        result_tags.append(
            tag.clone(frame_range=[tag_start - start, tag_end - start], key=tag.key())
        )
    return result_tags


def clip_annotation(ann: VideoAnnotation, start: int, end: int) -> VideoAnnotation:
    """Annotation of frames start..end (inclusive), re-indexed so that `start` becomes frame 0."""
    frames = []
    for frame in ann.frames:
        if start <= frame.index <= end:
            index = frame.index - start
            figures = [figure.clone(frame_index=index) for figure in frame.figures]
            frames.append(frame.clone(index=index, figures=figures))
    video_tags, frame_range_tags = get_ann_tags(ann)
    tags = deepcopy(video_tags)
    tags.extend(get_frame_range_tags(frame_range_tags, start, end))
    return ann.clone(
        frames_count=end - start + 1,
        frames=FrameCollection(frames),
        tags=VideoTagCollection(tags),
    )


def get_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        import imageio_ffmpeg

        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    return ffmpeg


def cut_clip(
    video_path: str,
    start: int,
    end: int,
    frames_to_timecodes: Optional[List[float]],
    clip_path: str,
    threads: int = 0,
) -> None:
    """Write frames start..end (inclusive) of the video to clip_path. The video is re-encoded
    (H.264, AAC), so the cut is frame exact whatever the keyframes are."""
    frames = end - start + 1
    cmd = [get_ffmpeg(), "-hide_banner", "-loglevel", "error", "-nostdin", "-y"]
    if frames_to_timecodes and len(frames_to_timecodes) > start:
        if start > 0:
            # Seek to the midpoint before the first frame: decoding resumes from the previous
            # keyframe and drops everything earlier, so the clip starts exactly at `start`.
            seek = (frames_to_timecodes[start - 1] + frames_to_timecodes[start]) / 2
            cmd += ["-ss", f"{seek:.6f}"]
        cmd += ["-i", video_path, "-map", "0:v:0", "-map", "0:a:0?"]
    else:
        # No timecodes: count decoded frames from the start of the video (slower, still exact).
        cmd += ["-i", video_path, "-map", "0:v:0", "-an"]
        cmd += ["-vf", f"select=between(n\\,{start}\\,{end}),setpts=PTS-STARTPTS"]
    cmd += [
        "-frames:v",
        str(frames),
        "-fps_mode",
        "passthrough",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
    ]
    if threads > 0:
        cmd += ["-threads", str(threads)]
    cmd.append(clip_path)
    os.makedirs(os.path.dirname(clip_path), exist_ok=True)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg could not cut frames {start}-{end}: {result.stderr.strip()}")


def make_new_video_info(video_info: VideoInfo, video_name: str, video_path: str) -> VideoInfo:
    """VideoInfo of a new local video file, based on the info of the video it was made from."""
    video = get_video_info(video_path)
    file_meta = deepcopy(video_info.file_meta) or {}
    file_meta["duration"] = video["duration"]
    file_meta["size"] = video["size"]
    file_meta["streams"] = video["streams"]
    for stream in video["streams"]:
        codec_type = stream.get("codec_type", None)
        if codec_type is None:
            codec_type = stream.get("codecType", None)
        if codec_type == "video":
            file_meta["framesCount"] = stream["framesCount"]
            file_meta["framesToTimecodes"] = stream["framesToTimecodes"]
            file_meta["height"] = stream["height"]
            file_meta["width"] = stream["width"]
            break

    return VideoInfo(
        id=None,
        name=video_name,
        hash=None,
        link=None,
        team_id=g.TEAM_ID,
        workspace_id=g.WORKSPACE_ID,
        project_id=None,
        dataset_id=None,
        path_original=None,
        frames_to_timecodes=file_meta["framesToTimecodes"],
        frames_count=file_meta["framesCount"],
        frame_width=file_meta["width"],
        frame_height=file_meta["height"],
        created_at=None,
        updated_at=None,
        tags=video_info.tags,
        file_meta=file_meta,
        meta=None,
        custom_data={},
        processing_path=None,
    )


def cut_clips(
    video_path: str,
    video_info: VideoInfo,
    ann: VideoAnnotation,
    ranges: Sequence[Tuple[int, int]],
    result_dir: Optional[str] = None,
    threads: int = 0,
) -> List[Clip]:
    """Cut one clip per inclusive (start, end) frame range of the video.

    Clips are named "<video name>_<n>.mp4" (n counts from 1, in the order of `ranges`). Each clip
    comes with its VideoInfo and its annotation: figures and frame range tags inside the range,
    re-indexed so that the first frame of the clip is frame 0. Video tags are kept as they are.

    :param video_path: local path of the source video, for example ``vid_desc.item_data``.
    :param video_info: VideoInfo of the source video, ``vid_desc.info.item_info``.
    :param ann: annotation of the source video.
    :param ranges: inclusive (start, end) frame ranges.
    :param result_dir: where to write the clips. Defaults to a folder per video in the app's
        data directory, which is cleared before every run.
    :param threads: ffmpeg threads per clip, 0 lets ffmpeg decide. Lower it when several videos
        are cut at the same time.
    """
    if result_dir is None:
        # Not in RESULTS_DIR: every folder there is archived as a result project after the run.
        result_dir = os.path.join(g.DATA_DIR, "clips", str(video_info.id or get_file_name(video_path)))
    if video_info.frames_count is None:
        video_info = make_new_video_info(video_info, video_info.name, video_path)
    ranges = normalize_ranges(ranges, video_info.frames_count)

    clips = []
    for idx, (start, end) in enumerate(ranges):
        clip_name = f"{get_file_name(video_info.name)}_{idx + 1}.mp4"
        clip_path = os.path.join(result_dir, clip_name)
        cut_clip(video_path, start, end, video_info.frames_to_timecodes, clip_path, threads)
        clip_info = make_new_video_info(video_info, clip_name, clip_path)
        clip_ann = clip_annotation(ann, start, end)
        if clip_info.frames_count != clip_ann.frames_count:
            logger.warning(
                f"Clip {clip_name} has {clip_info.frames_count} frames, expected "
                f"{clip_ann.frames_count}. Its annotation is trimmed to the clip."
            )
            last = start + min(clip_info.frames_count, clip_ann.frames_count) - 1
            clip_ann = clip_annotation(ann, start, last)
        clips.append(Clip(clip_path, clip_name, clip_info, clip_ann, start, end))
    return clips


def clip_to_item(vid_desc: VideoDescriptor, clip: Clip) -> Tuple[VideoDescriptor, VideoAnnotation]:
    """A pipeline item (descriptor, annotation) for a clip cut from the video of `vid_desc`.
    Yield it from a node to pass the clip to the next nodes."""
    item_name, item_ext = os.path.splitext(clip.name)
    clip_desc = VideoDescriptor(
        LegacyProjectItem(
            project_name=vid_desc.get_pr_name(),
            ds_name=vid_desc.get_ds_name(),
            ds_info=vid_desc.get_ds_info(),
            item_name=item_name,
            item_info=clip.info,
            ia_data={"item_ext": item_ext},
            item_path=clip.path,
            ann_path="",
        ),
        vid_desc.item_idx,
        False,
    )
    clip_desc.res_ds_name = vid_desc.res_ds_name
    clip_desc.update_item(clip.path)
    return clip_desc, clip.ann
