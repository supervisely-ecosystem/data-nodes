# coding: utf-8

from typing import Tuple
from skimage.morphology import remove_small_objects

from supervisely import Bitmap, Annotation, Label

from src.compute.Layer import Layer
from src.compute.dtl_utils import apply_to_labels
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from src.exceptions import WrongGeometryError


class DropNoiseFromBitmapLayer(Layer):
    action = "drop_noise"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["classes", "min_area", "src_type"],
                "properties": {
                    "classes": {"type": "array", "items": {"type": "string"}},
                    "min_area": {"type": "string", "pattern": "^[0-9]+(\.[0-9][0-9]?)?(%)|(px)$"},
                    "src_type": {"type": "string", "enum": ["image", "bbox"]},
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def modifies_data(self):
        return True

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el
        imsize_wh = ann.img_size[::-1]

        img_area = float(imsize_wh[0] * imsize_wh[1])
        area_str = self.settings["min_area"]

        def drop_noise(label: Label):
            if label.obj_class.name not in self.settings["classes"]:
                return [label]

            if not isinstance(label.geometry, Bitmap):
                raise WrongGeometryError(
                    None,
                    "Bitmap",
                    label.geometry.geometry_name(),
                    extra={"layer": self.action},
                )

            if area_str.endswith("%"):
                if self.settings["src_type"] == "image":
                    refer_area = img_area
                else:
                    refer_area = label.geometry.to_bbox().area

                area_part = float(area_str[: -len("%")]) / 100.0
                req_area = int(refer_area * area_part)
            else:
                req_area = int(area_str[: -len("px")])

            old_origin, old_mask = label.geometry.origin, label.geometry.data
            res_mask = remove_small_objects(old_mask, req_area)
            new_geometry = Bitmap(res_mask, old_origin)
            new_label = Label(geometry=new_geometry, obj_class=label.obj_class)
            return [new_label]

        ann = apply_to_labels(ann, drop_noise)
        yield img_desc, ann
