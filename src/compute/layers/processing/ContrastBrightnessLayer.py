# coding: utf-8

import numpy as np

from src.compute.Layer import Layer
from src.exceptions import BadSettingsError


class ContrastBrightnessLayer(Layer):
    action = "contrast_brightness"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["contrast", "brightness"],
                "properties": {
                    "contrast": {
                        "type": "object",
                        "required": ["min", "max"],
                        "properties": {
                            "min": {"type": "number", "minimum": 0, "maximum": 10},
                            "max": {"type": "number", "minimum": 0, "maximum": 10},
                            "center_grey": {"type": "boolean"},
                        },
                    },
                    "brightness": {
                        "type": "object",
                        "required": ["min", "max"],
                        "properties": {
                            "min": {"type": "number", "minimum": -255, "maximum": 255},
                            "max": {"type": "number", "minimum": -255, "maximum": 255},
                        },
                    },
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def validate(self):
        super().validate()

        def check_min_max(dictionary, text):
            if dictionary["min"] > dictionary["max"]:
                raise BadSettingsError('"min" should be <= than "max" for "{}"'.format(text))

        check_min_max(self.settings["contrast"], "contrast")
        check_min_max(self.settings["brightness"], "brightness")

    def requires_item(self):
        return True

    def modifies_data(self):
        return True

    def process(self, data_el):
        img_desc, ann_orig = data_el

        contrast_b = self.settings["contrast"]
        contrast_value = np.random.uniform(contrast_b["min"], contrast_b["max"])
        if contrast_b.get("center_grey", False):
            contrast_c = 128
        else:
            contrast_c = 0

        brightness_b = self.settings["brightness"]
        brightness_value = np.random.uniform(brightness_b["min"], brightness_b["max"])

        img = img_desc.read_image()
        img = img.astype(np.float32)
        img = (img - contrast_c) * float(contrast_value) + (brightness_value + contrast_c)

        img = np.clip(img, 0, 255).astype(np.uint8)
        new_img_desc = img_desc.clone_with_item(img)
        yield new_img_desc, ann_orig
