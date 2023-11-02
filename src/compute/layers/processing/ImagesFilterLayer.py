# coding: utf-8

from typing import Tuple

from supervisely import Annotation, Label

from src.compute.Layer import Layer
from src.compute.dtl_utils.image_descriptor import ImageDescriptor
from src.compute.dtl_utils import apply_to_labels


class ImagesFilterLayer(Layer):
    action = "images_filter"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["filter_by"],
                "properties": {
                    "filter_by": {
                        "maxItems": 1,
                        "oneOf": [
                            {
                                "type": "object",
                                "required": ["names"],
                                "properties": {
                                    "names": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    }
                                },
                            },
                            {
                                "type": "object",
                                "required": ["polygon_sizes"],
                                "properties": {
                                    "polygon_sizes": {
                                        "type": "object",
                                        "required": [
                                            "filtering_classes",
                                            "area_size",
                                            "action",
                                            "comparator",
                                        ],
                                        "properties": {
                                            "filtering_classes": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                            "area_size": {
                                                "oneOf": [
                                                    {
                                                        "type": "object",
                                                        "required": ["percent"],
                                                        "properties": {
                                                            "percent": {
                                                                "$ref": "#/definitions/percent"
                                                            }
                                                        },
                                                    },
                                                    {
                                                        "type": "object",
                                                        "required": ["height", "width"],
                                                        "properties": {
                                                            "width": {"type": "integer"},
                                                            "height": {"type": "integer"},
                                                        },
                                                    },
                                                ]
                                            },
                                            "action": {
                                                "oneOf": [
                                                    {
                                                        "type": "object",
                                                        "required": ["remap_class"],
                                                        "properties": {
                                                            "remap_class": {"type": "string"},
                                                        },
                                                    },
                                                    {"type": "string", "enum": ["delete"]},
                                                ]
                                            },
                                            "comparator": {
                                                "type": "string",
                                                "enum": ["less", "greater"],
                                            },
                                        },
                                    }
                                },
                            },
                        ],
                    }
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el

        img_area = float(ann.img_size[0] * ann.img_size[1])
        area_set = []

        # @TODO: use operator.lt / operator.gt

        def filter_by_names(label: Label):
            if label.obj_class.name not in self.settings["filter_by"]["names"]:
                return []  # action 'delete'
            return [label]

        def filter_delete_percent(label: Label):
            if self.settings["filter_by"]["polygon_sizes"]["comparator"] == "less":
                compar = lambda x: x < area_set["percent"]
            else:
                compar = lambda x: x > area_set["percent"]

            if (
                label.obj_class.name
                in self.settings["filter_by"]["polygon_sizes"]["filtering_classes"]
            ):
                label_area = label.area
                area_percent = 100.0 * label_area / img_area
                if compar(area_percent):  # satisfied condition
                    return []  # action 'delete'
            return [label]

        def filter_delete_size(label: Label):
            if self.settings["filter_by"]["polygon_sizes"]["comparator"] == "less":
                compar = lambda x: x.width < area_set["width"] or x.height < area_set["height"]
            else:
                compar = lambda x: x.width > area_set["width"] or x.height > area_set["height"]

            if (
                label.obj_class.name
                in self.settings["filter_by"]["polygon_sizes"]["filtering_classes"]
            ):
                rect = label.geometry.to_bbox()
                if compar(rect):  # satisfied condition
                    return []  # action 'delete'
            return [label]

        if "names" in self.settings["filter_by"]:
            ann = apply_to_labels(ann, filter_by_names)
            yield img_desc, ann
        else:
            area_set = self.settings["filter_by"]["polygon_sizes"]["area_size"]
            if "percent" in area_set:
                ann = apply_to_labels(ann, filter_delete_percent)
            else:
                ann = apply_to_labels(ann, filter_delete_size)

            yield img_desc, ann
