# coding: utf-8

from typing import Tuple
import cv2
import numpy as np

from supervisely import Bitmap, Polygon, Annotation, Label

from src.compute.Layer import Layer
from src.compute.classes_utils import ClassConstants
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from src.compute.dtl_utils import apply_to_labels
from src.exceptions import WrongGeometryError


# FigureBitmap to FigurePolygon
class MaskToPolygonLayer(Layer):
    action = "mask_to_polygon"
    legacy_action = "bitmap2poly"

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
                    },
                    "approx_epsilon": {"type": "number", "minimum": 0},
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def define_classes_mapping(self):
        for old_class, new_class in self.settings["classes_mapping"].items():
            self.cls_mapping[old_class] = {"title": new_class, "shape": Polygon.geometry_name()}
        self.cls_mapping[ClassConstants.OTHER] = ClassConstants.DEFAULT

    def modifies_data(self):
        return True

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el
        approx_epsilon = self.settings.get("approx_epsilon")

        def to_contours(label: Label):
            new_title = self.settings["classes_mapping"].get(label.obj_class.name, None)
            if new_title is None:
                return [label]
            if not isinstance(label.geometry, Bitmap):
                raise WrongGeometryError(
                    None,
                    "Bitmap",
                    label.geometry.geometry_name(),
                    extra={"layer": self.action},
                )

            origin = label.geometry.origin
            mask = label.geometry.data
            contours, hier = cv2.findContours(
                mask.astype(np.uint8),
                mode=cv2.RETR_CCOMP,  # two-level hierarchy, to get polygons with holes
                method=cv2.CHAIN_APPROX_SIMPLE,
            )
            if (hier is None) or (contours is None):
                return []

            res = []
            for idx, hier_pos in enumerate(hier[0]):
                next_idx, prev_idx, child_idx, parent_idx = hier_pos
                if parent_idx < 0:
                    external = contours[idx][:, 0]
                    internals = []
                    while child_idx >= 0:
                        internals.append(contours[child_idx][:, 0])
                        child_idx = hier[0][child_idx][0]

                    new_obj_class = label.obj_class.clone(name=new_title, geometry_type=Polygon)
                    new_geometry = (
                        Polygon(
                            exterior=[(p[1], p[0]) for p in external],
                            interior=[[(p[1], p[0]) for p in internal] for internal in internals],
                        )
                        .translate(origin.row, origin.col)
                        .approx_dp(approx_epsilon)
                    )

                    res.append(label.clone(geometry=new_geometry, obj_class=new_obj_class))

            # offset = (origin[0] + .5, origin[1] + .5)
            # for x in res:
            #     x.shift(offset)

            return res

        ann = apply_to_labels(ann, to_contours)
        yield img_desc, ann
