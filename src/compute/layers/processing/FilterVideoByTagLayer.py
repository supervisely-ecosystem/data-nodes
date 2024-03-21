# coding: utf-8

from typing import List, Tuple, Union

from supervisely import VideoAnnotation

from src.compute.Layer import Layer
from src.compute.dtl_utils.item_descriptor import VideoDescriptor
from supervisely import Tag, TagCollection


class FilterVideoByTagLayer(Layer):
    action = "filter_videos_by_tag"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["tags", "condition"],
                "properties": {
                    "tags": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["name", "value"],
                            "properties": {
                                "name": {"type": "string"},
                                "value": {},
                            },
                        },
                    },
                    "condition": {"type": "string", "enum": ["with", "without"]},
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

        satisfies_cond = False
        condition = self.settings["condition"]

        def set_condition(
            video_tags: Union[List[Tag], TagCollection], filter_tags: List[dict], condition: str
        ):
            if all(name in video_tags for name in filter_tags) and condition == "with":
                return True
            elif all(name not in video_tags for name in filter_tags) and condition == "without":
                return True

        video_tags = [{"name": tag.name, "value": tag.value} for tag in ann.tags.items()]

        satisfies_cond = set_condition(video_tags, self.settings["tags"], condition)

        if satisfies_cond:
            yield data_el + tuple([0])  # Output True
        else:
            yield data_el + tuple([1])  # Output False
