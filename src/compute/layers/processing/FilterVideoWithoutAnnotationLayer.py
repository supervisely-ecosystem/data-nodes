# coding: utf-8

from typing import Tuple

from supervisely import VideoAnnotation, Frame, VideoObject, VideoFigure

from src.compute.Layer import Layer
from src.compute.dtl_utils.item_descriptor import VideoDescriptor


class FilterVideoWithoutAnnotationLayer(Layer):
    action = "filter_video_without_annotation"

    layer_settings = {
        "required": ["settings"],
        "properties": {"settings": {}},
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def modifies_data(self):
        return False

    def process(self, data_el: Tuple[VideoDescriptor, VideoAnnotation]):
        vid_desc, ann = data_el
        ann: VideoAnnotation

        if len(ann.objects) == 0 and len(ann.tags) == 0:
            yield data_el + tuple([0])  # True
        else:
            yield data_el + tuple([1])  # False
