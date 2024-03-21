# coding: utf-8

from typing import Tuple

from supervisely import VideoAnnotation

from src.compute.Layer import Layer
from src.compute.dtl_utils.item_descriptor import VideoDescriptor


class FilterVideoByObjectLayer(Layer):
    action = "filter_videos_by_object"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["include", "exclude"],
                "properties": {
                    "include": {"type": "array", "items": {"type": "string"}},
                    "exclude": {"type": "array", "items": {"type": "string"}},
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def modifies_data(self):
        return False

    def process(self, data_el: Tuple[VideoDescriptor, VideoAnnotation]):
        _, ann = data_el

        satisfies_cond = True
        include_classes = self.settings["include"]
        exclude_classes = self.settings["exclude"]
        video_classes = []

        if self.net.preview_mode:
            yield data_el + tuple([0])  # Output
        else:
            for v_object in ann.objects.items():
                video_classes.append(v_object.obj_class.name)

            if exclude_classes and not include_classes:
                if any(name in video_classes for name in exclude_classes):
                    satisfies_cond = False

            elif include_classes and not exclude_classes:
                if any(name not in video_classes for name in include_classes):
                    satisfies_cond = False

            elif include_classes and exclude_classes:
                if any(name not in video_classes for name in include_classes) or any(
                    name in video_classes for name in exclude_classes
                ):
                    satisfies_cond = False

            if satisfies_cond:
                yield data_el + tuple([0])  # Output True
            else:
                yield data_el + tuple([1])  # Output False
