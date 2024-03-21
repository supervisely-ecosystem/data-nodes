# coding: utf-8

from typing import Tuple

from supervisely import Annotation, Label

from src.compute.Layer import Layer
from src.compute.classes_utils import ClassConstants
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from src.compute.dtl_utils import apply_to_labels


class DropObjectByClassLayer(Layer):
    action = "drop_object_by_class"
    legacy_action = "drop_obj_by_class"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["classes"],
                "properties": {"classes": {"type": "array", "items": {"type": "string"}}},
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def define_classes_mapping(self):
        for cls in self.settings["classes"]:
            self.cls_mapping[cls] = ClassConstants.IGNORE
        self.cls_mapping[ClassConstants.OTHER] = ClassConstants.DEFAULT

    def obj_filter(self, label: Label):
        if label.obj_class.name in self.settings["classes"]:
            return []
        return [label]

    def modifies_data(self):
        return True

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el

        ann = apply_to_labels(ann, self.obj_filter)
        yield img_desc, ann
