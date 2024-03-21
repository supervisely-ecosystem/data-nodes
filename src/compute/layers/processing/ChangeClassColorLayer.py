# coding: utf-8

from typing import Tuple

from supervisely import Annotation

from src.compute.Layer import Layer
from src.compute.classes_utils import ClassConstants
from src.compute.dtl_utils.item_descriptor import ImageDescriptor


class ChangeClassColorLayer(Layer):
    action = "change_class_color"
    legacy_action = "color_class"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["classes_color_mapping"],
                "properties": {
                    "classes_color_mapping": {
                        "type": "object",
                        "patternProperties": {
                            ".*": {
                                "oneOf": [
                                    {
                                        "type": "string",
                                        "pattern": "^#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$",
                                    },
                                    {
                                        "type": "array",
                                        "items": {"type": "number", "minimum": 0, "maximum": 255},
                                        "maxItems": 3,
                                        "minItems": 3,
                                    },
                                ]
                            }
                        },
                    }
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def define_classes_mapping(self):
        classes_color_mapping = self.settings["classes_color_mapping"]
        self.cls_mapping[ClassConstants.UPDATE] = [
            {"title": class_name, "color": class_color}
            for class_name, class_color in classes_color_mapping.items()
        ]

        self.cls_mapping[ClassConstants.OTHER] = ClassConstants.DEFAULT

    def modifies_data(self):
        return True

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el
        ann = Annotation.from_json(ann.to_json(), self.output_meta)
        yield img_desc, ann
