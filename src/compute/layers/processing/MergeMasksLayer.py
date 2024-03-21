# coding: utf-8

from typing import List, Tuple
import numpy as np

from supervisely import Bitmap, Annotation, Label

from src.compute.Layer import Layer
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from src.exceptions import WrongGeometryError


class MergeMasksLayer(Layer):
    action = "merge_masks"
    legacy_action = "merge_bitmap_masks"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["class"],
                "properties": {"class": {"type": "string"}},
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def merge_bitmaps(self, bitmaps: List[Bitmap], img_size):
        base_mask = np.zeros(img_size, bool)
        for label in bitmaps:
            label.draw(base_mask, color=True)

        return Bitmap(base_mask)

    def modifies_data(self):
        return True

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el
        img_size = ann.img_size

        class_mask = self.settings["class"]

        bitmaps_for_merge = []
        new_labels = []
        obj_class = None

        for label in ann.labels:
            if label.obj_class.name == class_mask:
                if not isinstance(label.geometry, Bitmap):
                    raise WrongGeometryError(
                        None,
                        "Bitmap",
                        label.geometry.geometry_name(),
                        extra={"layer": self.action},
                    )
                bitmaps_for_merge.append(label.geometry)
                obj_class = label.obj_class
            else:
                new_labels.append(label)

        # speed optimize
        if len(bitmaps_for_merge) > 0:
            if len(bitmaps_for_merge) == 1:
                new_labels.append(Label(geometry=bitmaps_for_merge[0], obj_class=obj_class))
            else:
                result_geometry = self.merge_bitmaps(bitmaps_for_merge, img_size)
                new_labels.append(Label(geometry=result_geometry, obj_class=obj_class))

        ann = ann.clone(labels=new_labels)
        yield img_desc, ann
