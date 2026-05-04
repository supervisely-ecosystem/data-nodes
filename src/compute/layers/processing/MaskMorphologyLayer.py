# coding: utf-8

from typing import Tuple

import cv2
import numpy as np

from supervisely import Annotation, Bitmap, Label, PointLocation

from src.compute.Layer import Layer
from src.compute.dtl_utils import apply_to_labels
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from src.exceptions import WrongGeometryError


class MaskMorphologyLayer(Layer):
    action = "mask_morphology"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["classes", "operation", "kernel_size", "kernel_shape", "iterations"],
                "properties": {
                    "classes": {"type": "array", "items": {"type": "string"}},
                    "operation": {
                        "type": "string",
                        "enum": ["open", "close", "erode", "dilate"],
                    },
                    "kernel_size": {"type": "integer", "minimum": 1},
                    "kernel_shape": {
                        "type": "string",
                        "enum": ["ellipse", "rectangle", "cross"],
                    },
                    "iterations": {"type": "integer", "minimum": 1},
                },
            }
        },
    }

    operation_mapping = {
        "open": cv2.MORPH_OPEN,
        "close": cv2.MORPH_CLOSE,
        "erode": cv2.MORPH_ERODE,
        "dilate": cv2.MORPH_DILATE,
    }
    kernel_shape_mapping = {
        "ellipse": cv2.MORPH_ELLIPSE,
        "rectangle": cv2.MORPH_RECT,
        "cross": cv2.MORPH_CROSS,
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def define_classes_mapping(self):
        super().define_classes_mapping()

    def modifies_data(self):
        return True

    @staticmethod
    def _crop_to_mask(mask: np.ndarray) -> Tuple[np.ndarray, PointLocation]:
        rows, cols = np.where(mask)
        top, bottom = rows.min(), rows.max() + 1
        left, right = cols.min(), cols.max() + 1
        return mask[top:bottom, left:right], PointLocation(row=int(top), col=int(left))

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el
        operation = self.operation_mapping[self.settings["operation"]]
        kernel_shape = self.kernel_shape_mapping[self.settings["kernel_shape"]]
        kernel_size = self.settings["kernel_size"]
        iterations = self.settings["iterations"]
        kernel = cv2.getStructuringElement(kernel_shape, (kernel_size, kernel_size))

        def apply_morphology(label: Label):
            if label.obj_class.name not in self.settings["classes"]:
                return [label]
            if not isinstance(label.geometry, Bitmap):
                raise WrongGeometryError(
                    None,
                    "Bitmap",
                    label.geometry.geometry_name(),
                    extra={"layer": self.action},
                )

            origin, mask = label.geometry.origin, label.geometry.data
            full_mask = np.zeros(ann.img_size, dtype=np.uint8)
            h, w = mask.shape[:2]
            full_mask[origin.row : origin.row + h, origin.col : origin.col + w] = mask.astype(
                np.uint8
            )

            res_mask = cv2.morphologyEx(
                full_mask,
                operation,
                kernel,
                iterations=iterations,
            ).astype(bool)

            if not np.any(res_mask):
                return []

            cropped_mask, new_origin = self._crop_to_mask(res_mask)
            new_geometry = Bitmap(cropped_mask, new_origin, extra_validation=False)
            return [label.clone(geometry=new_geometry)]

        ann = apply_to_labels(ann, apply_morphology)
        yield img_desc, ann
