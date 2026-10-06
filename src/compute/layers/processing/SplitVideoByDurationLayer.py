# coding: utf-8

from typing import List, Tuple

from supervisely import VideoAnnotation
from supervisely.api.video.video_api import VideoInfo

from src.compute.Layer import Layer
from src.compute.dtl_utils.item_descriptor import VideoDescriptor
from src.compute.utils.video_clips import clip_to_item, cut_clips


# Split functions: inclusive (start, end) frame ranges


def get_frames_ranges(split_frames: int, frames_count: int) -> List[Tuple[int, int]]:
    return [
        (start, min(start + split_frames, frames_count) - 1)
        for start in range(0, frames_count, split_frames)
    ]


def get_time_ranges(split_sec: float, video_info: VideoInfo) -> List[Tuple[int, int]]:
    timecodes = video_info.frames_to_timecodes
    if not timecodes:
        fps = video_info.frames_count / video_info.duration
        timecodes = [idx / fps for idx in range(video_info.frames_count)]
    # frame -> number of the part that contains its timecode
    parts = [int(timecode // split_sec) for timecode in timecodes]
    ranges = []
    start = 0
    for idx in range(1, len(parts) + 1):
        if idx == len(parts) or parts[idx] != parts[start]:
            ranges.append((start, idx - 1))
            start = idx
    return ranges


# -----------------


class SplitVideobyDurationLayer(Layer):
    action = "split_video_by_duration"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["duration_unit", "split_step"],
                "properties": {
                    "duration_unit": {
                        "type": "string",
                        "enum": [
                            "frames",
                            "seconds",
                        ],
                    },
                    "split_step": {"type": "integer", "minimum": 0},
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def modifies_data(self):
        return True

    def process(self, data_el: Tuple[VideoDescriptor, VideoAnnotation]):
        vid_desc, ann = data_el
        ann: VideoAnnotation

        duration_unit = self.settings["duration_unit"]
        split_step = self.settings["split_step"]
        video_info: VideoInfo = vid_desc.info.item_info

        if not self.net.preview_mode:
            if duration_unit == "frames":
                if split_step >= video_info.frames_count:
                    # Frames count set for splitting, is more then video
                    yield (vid_desc, ann)
                    return
                ranges = get_frames_ranges(split_step, video_info.frames_count)
            else:
                if split_step >= video_info.duration:
                    # Time set for splitting, is more then video
                    yield (vid_desc, ann)
                    return
                ranges = get_time_ranges(split_step, video_info)

            for clip in cut_clips(vid_desc.item_data, video_info, ann, ranges):
                yield clip_to_item(vid_desc, clip)
        else:
            yield vid_desc, ann
