# coding: utf-8

from typing import Tuple

from supervisely import VideoAnnotation
from src.compute.Layer import Layer
from src.compute.dtl_utils.item_descriptor import VideoDescriptor


class FilterVideobyDurationLayer(Layer):
    action = "filter_video_by_duration"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["duration_unit", "duration_threshold"],
                "properties": {
                    "duration_unit": {
                        "type": "string",
                        "enum": [
                            "frames",
                            "seconds",
                        ],
                    },
                    "duration_threshold": {"type": "integer", "minimum": 0},
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def modifies_data(self):
        return False

    def process(self, data_el: Tuple[VideoDescriptor, VideoAnnotation]):
        vid_desc, ann = data_el
        ann: VideoAnnotation

        duration_unit = self.settings["duration_unit"]
        duration_threshold = self.settings["duration_threshold"]

        if not self.net.preview_mode:
            # by frames
            if duration_unit == "frames":
                if (
                    vid_desc.info.item_info.frames_count <= duration_threshold
                ):  # take duration from local video?
                    yield data_el + tuple([0])  # True
                else:
                    yield data_el + tuple([1])  # False
            else:
                if (
                    vid_desc.info.item_info.duration <= duration_threshold
                ):  # take duration from local video?
                    yield data_el + tuple([0])  # True
                else:
                    yield data_el + tuple([1])  # False
        else:
            yield data_el + tuple([0])
