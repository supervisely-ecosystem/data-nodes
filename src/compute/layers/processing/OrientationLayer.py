# coding: utf-8

from typing import Tuple

from supervisely import Annotation, aug

from src.compute.Layer import Layer
from src.compute.dtl_utils.item_descriptor import ImageDescriptor


class OrientationLayer(Layer):
    action = "orientation"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["target_orientation", "rotation_direction"],
                "properties": {
                    "target_orientation": {
                        "type": "string",
                        "enum": ["landscape", "portrait"],
                    },
                    "rotation_direction": {
                        "type": "string",
                        "enum": ["clockwise", "counter_clockwise"],
                    },
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def requires_item(self):
        return True

    def modifies_data(self):
        return True

    def _should_rotate(self, img_size: Tuple[int, int]) -> bool:
        img_h, img_w = img_size
        target_orientation = self.settings["target_orientation"]

        if img_h == img_w:
            return False

        if target_orientation == "landscape":
            return img_h > img_w

        return img_w > img_h

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el

        if not self._should_rotate(ann.img_size):
            yield img_desc, ann
            return

        rotation_direction = self.settings["rotation_direction"]
        rotate_degrees = -90 if rotation_direction == "clockwise" else 90

        img = img_desc.read_image()
        new_img, new_ann = aug.rotate(
            img,
            ann,
            degrees=rotate_degrees,
            mode=aug.RotationModes.KEEP,
        )

        yield img_desc.clone_with_item(new_img), new_ann
