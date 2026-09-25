# coding: utf-8

from supervisely import Label

from src.compute.Layer import Layer
from src.compute.classes_utils import (
    ClassConstants,
    get_merge_nodes_mapping,
    remap_graph_nodes,
)
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
            dst_obj_class = None
            if self.output_meta is not None:
                dst_obj_class = self.output_meta.get_obj_class(new_class)
            if dst_obj_class is None:
                label = label.clone(obj_class=label.obj_class.clone(name=new_class))
                return [label]
            geometry = label.geometry
            nodes_mapping = get_merge_nodes_mapping(label.obj_class, dst_obj_class)
            if nodes_mapping is not None:
                geometry = remap_graph_nodes(geometry, nodes_mapping)
            label = label.clone(geometry=geometry, obj_class=dst_obj_class)
            return [label]

    def modifies_data(self):
        return True

    def process(self, data_el):
        img_desc, ann = data_el
        ann = apply_to_labels(ann, self.class_mapper)
        yield img_desc, ann
