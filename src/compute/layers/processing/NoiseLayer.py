# coding: utf-8

import numpy as np

from src.compute.Layer import Layer


class NoiseLayer(Layer):
    action = "noise"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["mean", "std"],
                "properties": {"mean": {"type": "number"}, "std": {"type": "number"}},
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def requires_item(self):
        return True

    def modifies_data(self):
        return True

    def process(self, data_el):
        img_desc, ann_orig = data_el

        img = img_desc.read_image()
        img = img.astype(np.float32)
        img += np.random.normal(self.settings["mean"], self.settings["std"], img.shape)

        img = np.clip(img, 0, 255).astype(np.uint8)
        new_img_desc = img_desc.clone_with_item(img)
        yield new_img_desc, ann_orig
