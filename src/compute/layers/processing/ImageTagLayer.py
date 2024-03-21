# coding: utf-8

from typing import Tuple

from supervisely import Annotation, Tag

from src.compute.Layer import Layer
from src.compute.dtl_utils.item_descriptor import ImageDescriptor


class ImageTagLayer(Layer):
    action = "image_tag"
    legacy_action = "tag"

    # TODO add a way to specify meta information for the added tag.
    # TODO support all tag value types.
    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["tag", "action"],
                "properties": {
                    "tag": {
                        "maxItems": 1,
                        "oneOf": [
                            {"type": "null"},
                            {"type": "string"},
                            {
                                "type": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {"type": "string"},
                                    "value": {},
                                },
                            },
                        ],
                    },
                    "action": {"type": "string", "enum": ["add", "delete"]},
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    @property
    def is_action_add(self):
        return self.settings["action"] == "add"

    @property
    def is_action_delete(self):
        return self.settings["action"] == "delete"

    @property
    def tag(self):
        if self.settings["tag"] is None:
            return None
        elif isinstance(self.settings["tag"], str):
            tag_name = self.settings["tag"]
            tag_value = None
        else:
            tag_name = self.settings["tag"]["name"]
            tag_value = self.settings["tag"]["value"]
        tag_meta = self.output_meta.tag_metas.get(tag_name)
        if tag_meta is None:
            raise ValueError("Tag {} is not present in the project meta".format(tag_name))
        try:
            return Tag(
                meta=tag_meta,
                value=tag_value,
            )
        except:
            raise ValueError("Tag value {} is not valid for tag {}".format(tag_value, tag_name))

    @property
    def tag_json(self):
        self.tag.to_json()

    def get_added_tag_metas(self):
        return []
        # return [self.tag_json] if self.is_action_add else []

    def get_removed_tag_metas(self):
        return []
        # return [self.tag_json] if self.is_action_delete else []

    def modifies_data(self):
        return True

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el

        dst_tag = self.tag
        if dst_tag is not None:
            if self.is_action_add:
                if dst_tag.name in [t.name for t in ann.img_tags]:
                    ann = ann.clone(
                        img_tags=[
                            dst_tag if tag.name == dst_tag.name else tag for tag in ann.img_tags
                        ]
                    )
                else:
                    ann = ann.clone(img_tags=[*[t for t in ann.img_tags], dst_tag])

            if self.is_action_delete:
                ann = ann.clone(img_tags=[t for t in ann.img_tags if t.name != dst_tag.name])

        yield img_desc, ann
