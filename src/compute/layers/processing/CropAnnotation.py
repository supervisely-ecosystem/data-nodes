# coding: utf-8

import random

from supervisely import logger, Rectangle

from src.compute.Layer import Layer
from src.exceptions import BadSettingsError


class CropAnnotationLayer(Layer):
    action = "crop_annotation"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "maxItems": 1,
                "oneOf": [
                    {
                        "type": "object",
                        "required": ["random_part"],
                        "properties": {
                            "random_part": {
                                "type": "object",
                                "required": ["height", "width"],
                                "properties": {
                                    "height": {
                                        "type": "object",
                                        "required": ["min_percent", "max_percent"],
                                        "properties": {
                                            "min_percent": {"$ref": "#/definitions/percent"},
                                            "max_percent": {"$ref": "#/definitions/percent"},
                                        },
                                    },
                                    "width": {
                                        "type": "object",
                                        "required": ["min_percent", "max_percent"],
                                        "properties": {
                                            "min_percent": {"$ref": "#/definitions/percent"},
                                            "max_percent": {"$ref": "#/definitions/percent"},
                                        },
                                    },
                                    "keep_aspect_ratio": {
                                        "type": "boolean",
                                        "default": False,
                                    },
                                },
                            }
                        },
                    },
                    {
                        "type": "object",
                        "required": ["sides"],
                        "properties": {
                            "sides": {
                                "type": "object",
                                "uniqueItems": True,
                                "items": {
                                    "type": "string",
                                    "patternProperties": {
                                        "(left)|(top)|(bottom)|(right)": {
                                            "type": "string",
                                            "pattern": "^[0-9]+(%)|(px)$",
                                        }
                                    },
                                },
                            }
                        },
                    },
                ],
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

        if "random_part" in self.settings:
            random_part = self.settings["random_part"]
            keep_aspect_ratio = random_part.get("keep_aspect_ratio", False)
            if keep_aspect_ratio:
                if random_part["height"] != random_part["width"]:
                    raise BadSettingsError(
                        "When 'keep_aspect_ratio' is 'true', 'height' and 'width' should be equal"
                    )

            def check_min_max(dictionary, text):
                if dictionary["min_percent"] > dictionary["max_percent"]:
                    raise BadSettingsError(
                        "'min_percent' should be <= than 'max_percent' for {}".format(text)
                    )

            check_min_max(random_part["height"], "height")
            check_min_max(random_part["width"], "width")

    def modifies_data(self):
        return True

    def process(self, data_el):
        img_desc, ann = data_el
        img_h, img_w = ann.img_size

        def rand_percent(min_percent, max_percent):
            the_percent = random.uniform(min_percent, max_percent)
            return the_percent

        def calc_paddings(length: int, perc):
            new_length = min(int(length), int(length * perc / 100.0))
            l_padding = random.randint(0, length - new_length)  # including [a; b]
            r_padding = length - l_padding - new_length
            return l_padding, r_padding

        def get_raw_size(side):
            if side in ("left", "right"):
                return img_w
            return img_h

        def get_padding_pixels(raw_side, side_padding_settings):
            if side_padding_settings is None:
                padding_pixels = 0
            elif side_padding_settings.endswith("px"):
                padding_pixels = int(side_padding_settings[: -len("px")])
            elif side_padding_settings.endswith("%"):
                padding_fraction = float(side_padding_settings[: -len("%")])
                padding_pixels = int(raw_side * padding_fraction / 100.0)
            else:
                raise ValueError(
                    'Unknown padding size format: {}. Expected absolute values as "5px" or relative as "5%"'.format(
                        side_padding_settings
                    )
                )

            return padding_pixels

        def is_empty_crop(img_h, img_w, paddings):
            return (
                paddings["left"] + paddings["right"] >= img_w
                or paddings["top"] + paddings["bottom"] >= img_h
            )

        def is_outside_crop(img_h, img_w, paddings):
            return (
                any(paddings[side] < 0 for side in paddings)
                or paddings["left"] >= img_w
                or paddings["right"] >= img_w
                or paddings["top"] >= img_h
                or paddings["bottom"] >= img_h
            )

        if "random_part" in self.settings:
            height_min_percent = self.settings["random_part"]["height"]["min_percent"]
            height_max_percent = self.settings["random_part"]["height"]["max_percent"]
            width_min_percent = self.settings["random_part"]["width"]["min_percent"]
            width_max_percent = self.settings["random_part"]["width"]["max_percent"]
            keep_aspect_ratio = self.settings["random_part"].get("keep_aspect_ratio", False)
            rand_percent_w = rand_percent(width_min_percent, width_max_percent)
            if not keep_aspect_ratio:
                rand_percent_h = rand_percent(height_min_percent, height_max_percent)
            else:
                rand_percent_h = rand_percent_w
            left, right = calc_paddings(img_w, rand_percent_w)
            top, bottom = calc_paddings(img_h, rand_percent_h)
            paddings = {"left": left, "right": right, "top": top, "bottom": bottom}
        elif "sides" in self.settings:
            paddings = {
                side: get_padding_pixels(get_raw_size(side), side_setting)
                for side, side_setting in self.settings["sides"].items()
            }
        else:
            raise NotImplemented("Crop layer: wrong params.")

        if is_empty_crop(img_h, img_w, paddings):
            logger.warning("Crop layer produced empty crop.")
            return  # no yield

        if is_outside_crop(img_h, img_w, paddings):
            raise RuntimeError("Crop layer: result crop bounds are outside of source image.")

        crop_rect = Rectangle(
            paddings["top"],
            paddings["left"],
            img_h - paddings["bottom"] - 1,
            img_w - paddings["right"] - 1,
        )
        ann = ann.relative_crop(crop_rect)
        yield img_desc, ann
