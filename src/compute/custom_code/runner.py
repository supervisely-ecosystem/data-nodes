"""Worker side of the Custom Code node.

Runs in the node's worker processes, so it must stay importable without src.globals, which
connects to the instance at import time. Only plain data (str, int, dict, list) crosses the
process boundary.
"""

import importlib.util
import os
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple

_modules = {}


def load_script(script_path: str):
    """Import the script once per worker process and check that it defines process()."""
    module = _modules.get(script_path)
    if module is None:
        spec = importlib.util.spec_from_file_location("ml_pipelines_custom_code", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not callable(getattr(module, "process", None)):
            raise ValueError(
                "The script must define a function "
                "process(video_path, video_info, ann, params) -> list of (start, end) frame ranges."
            )
        _modules[script_path] = module
    return module


def check_script(script_path: str) -> None:
    load_script(script_path)


def normalize_ranges(ranges, frames_count: int) -> List[Tuple[int, int]]:
    """Validate what process() returned: inclusive (start, end) frame ranges inside the video."""
    if ranges is None:
        raise ValueError("process() returned None. Return [] to drop the video.")
    result = []
    for frame_range in ranges:
        try:
            start, end = frame_range
            start, end = int(start), int(end)
        except (TypeError, ValueError):
            raise ValueError(
                f"process() returned {frame_range!r}: each range must be a (start, end) pair of frame indexes."
            )
        if not 0 <= start <= end < frames_count:
            raise ValueError(
                f"process() returned the range ({start}, {end}), outside the video's frames 0..{frames_count - 1}."
            )
        result.append((start, end))
    return result


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
    """Cut frames start..end (inclusive) into clip_path, re-encoded so the cut is frame exact."""
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


def run_video(
    script_path: str,
    video_path: str,
    video_info: Dict,
    ann_json: Dict,
    meta_json: Dict,
    params: Dict,
    clips_dir: str,
    ffmpeg_threads: int = 0,
) -> Dict:
    """Run the script's process() on one video and cut a clip for every range it returns.

    Returns {"ranges": [[start, end], ...], "clips": [[start, end, clip_path], ...]}. "clips" is
    empty when the video is dropped ([]) or passed through (one range over the whole video).
    """
    from supervisely import ProjectMeta, VideoAnnotation
    from supervisely.api.video.video_api import VideoInfo
    from supervisely.io.fs import get_file_name

    module = load_script(script_path)
    info = VideoInfo(**video_info)
    ann = VideoAnnotation.from_json(ann_json, ProjectMeta.from_json(meta_json))

    frames_count = info.frames_count
    if not frames_count:
        raise ValueError(f"Video {info.name} has no frames count in its metadata.")
    ranges = normalize_ranges(module.process(video_path, info, ann, params), frames_count)

    clips = []
    if ranges != [(0, frames_count - 1)]:
        base_name = get_file_name(info.name)
        for start, end in ranges:
            clip_name = f"{base_name}_frames_{start}-{end}.mp4"
            clip_path = os.path.join(clips_dir, str(info.id), clip_name)
            cut_clip(video_path, start, end, info.frames_to_timecodes, clip_path, ffmpeg_threads)
            clips.append([start, end, clip_path])
    return {"ranges": [list(r) for r in ranges], "clips": clips}
