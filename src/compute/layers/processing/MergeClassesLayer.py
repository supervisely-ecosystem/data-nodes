# coding: utf-8

from supervisely import Label

from src.compute.Layer import Layer
from src.compute.classes_utils import ClassConstants
from src.compute.dtl_utils import apply_to_labels
from src.exceptions import BadSettingsError


class MergeClassesLayer(Layer):
    action = "merge_classes"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["classes_mapping"],
                "properties": {
                    "classes_mapping": {
                        "type": "object",
                        "patternProperties": {".*": {"type": "string"}},
                    }
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def define_classes_mapping(self):
        self.cls_mapping = self.settings["classes_mapping"]
        self.cls_mapping[ClassConstants.OTHER] = ClassConstants.DEFAULT

    def class_mapper(self, label: Label):
        curr_class = label.obj_class.name

        if curr_class in self.cls_mapping:
            new_class = self.cls_mapping[curr_class]
            new_class = new_class.replace(ClassConstants.MERGE, "")
        else:
            raise BadSettingsError("Can not find mapping for class", extra={"class": curr_class})

        if new_class == ClassConstants.IGNORE:
            return []  # drop the figure
        elif new_class == ClassConstants.DEFAULT:
            return [label]  # don't change
        else:
            label = label.clone(obj_class=label.obj_class.clone(name=new_class))
            return [label]

    def modifies_data(self):
        return True

    def process(self, data_el):
        img_desc, ann = data_el
        ann = apply_to_labels(ann, self.class_mapper)
        yield img_desc, ann
