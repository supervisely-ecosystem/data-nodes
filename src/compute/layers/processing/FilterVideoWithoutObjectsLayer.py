# coding: utf-8

from typing import Tuple

from supervisely import VideoAnnotation, Frame, VideoObject, VideoFigure

from src.compute.Layer import Layer
from src.compute.dtl_utils.item_descriptor import VideoDescriptor


class FilterVideoWithoutObjectsLayer(Layer):
    action = "filter_video_without_objects"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["exclude_classes"],
                "properties": {
                    "exclude_classes": {"type": "array", "items": {"type": "string"}},
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

        satisfies_cond = False
        exclude_classes = self.settings["exclude_classes"]
        for object in ann.objects:
            object: VideoObject
            if object.obj_class.name in exclude_classes:
                satisfies_cond = True
                break

        if satisfies_cond:
            yield data_el + tuple([1])  # False
        else:
            yield data_el + tuple([0])  # True
