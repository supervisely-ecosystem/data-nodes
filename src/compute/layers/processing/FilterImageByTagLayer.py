# coding: utf-8

from typing import List, Tuple, Union

from supervisely import Annotation

from src.compute.Layer import Layer
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from supervisely import Tag, TagCollection


class FilterImageByTagLayer(Layer):
    action = "filter_image_by_tag"

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

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el
        condition = self.settings["condition"]

        def has_tag(img_tags: Union[List[Tag], TagCollection], filter_tag: dict):
            for img_tag in img_tags:
                if img_tag.name == filter_tag["name"] and img_tag.value == filter_tag["value"]:
                    return True
            return False

        if condition == "with":
            satisfies_cond = all(has_tag(ann.img_tags, f_tag) for f_tag in self.settings["tags"])
        elif condition == "without":
            satisfies_cond = all(
                not has_tag(ann.img_tags, f_tag) for f_tag in self.settings["tags"]
            )
        else:
            raise NotImplementedError()
        if satisfies_cond:
            yield data_el + tuple([0])  # branch 0
        else:
            yield data_el + tuple([1])  # branch 1
