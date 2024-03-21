from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import NodesFlow, Slider, Text, Checkbox, Switch, Container
from src.ui.dtl import PixelLevelAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs, get_slider_style, get_text_font_size


class ContrastBrightnessAction(PixelLevelAction):
    name = "contrast_brightness"
    title = "Contrast / Brightness"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/transformation-layers/contrast_brightness"
    description = (
        "This layer (contrast_brightness) randomly changes contrast and brightness of images. "
    )
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        # region contrast-widgets
        contrast_text = Text("Contrast", status="text", font_size=get_text_font_size())
        contrast_switch = Switch()
        contrast_container = Container(
            widgets=[contrast_text, contrast_switch],
            direction="horizontal",
            gap=0,
            fractions=[1, 3],
            style="place-items: center; padding: 6px",
        )

        DEFAULT_CONTRAST = [0, 1]
        contrast_slider = Slider(
            min=0, max=10, step=0.1, value=DEFAULT_CONTRAST, range=True, style=get_slider_style()
        )
        contrast_slider.hide()

        center_grey_text = Text("Center grey", status="text", font_size=get_text_font_size())
        center_grey_checkbox = Checkbox(center_grey_text)
        center_grey_checkbox.hide()
        contrast_preview_widget = Text(
            f"min: {DEFAULT_CONTRAST[0]} - max: {DEFAULT_CONTRAST[1]}",
            status="text",
            font_size=get_text_font_size(),
        )
        contrast_preview_widget.hide()

        @contrast_switch.value_changed
        def contrast_checkbox_value_changed(is_switched):
            if is_switched:
                contrast_slider.show()
                center_grey_checkbox.show()
                contrast_preview_widget.show()
            else:
                center_grey_checkbox.uncheck()
                contrast_slider.hide()
                center_grey_checkbox.hide()
                contrast_preview_widget.hide()

        @contrast_slider.value_changed
        def contrast_slider_value_changed(value):
            contrast_preview_widget.text = f"min: {value[0]} - max: {value[1]}"

        brightness_text = Text("Brightness", status="text", font_size=get_text_font_size())
        brightness_switch = Switch()
        brightness_container = Container(
            widgets=[brightness_text, brightness_switch],
            direction="horizontal",
            gap=0,
            fractions=[1, 3],
            style="place-items: center; padding: 6px",
        )

        DEFAULT_BRIGHTNESS = [-20, 20]
        brightness_slider = Slider(
            min=-255,
            max=255,
            step=1,
            value=DEFAULT_BRIGHTNESS,
            range=True,
            style=get_slider_style(),
        )
        brightness_slider.hide()

        brightness_preview_widget = Text(
            f"min: {DEFAULT_BRIGHTNESS[0]} - max: {DEFAULT_BRIGHTNESS[1]}",
            status="text",
            font_size=get_text_font_size(),
        )
        brightness_preview_widget.hide()

        @brightness_switch.value_changed
        def brightness_checkbox_value_changed(is_switched):
            if is_switched:
                brightness_slider.show()
                brightness_preview_widget.show()
            else:
                brightness_slider.hide()
                brightness_preview_widget.hide()

        @brightness_slider.value_changed
        def brightness_slider_value_changed(value):
            brightness_preview_widget.text = f"min: {value[0]} - max: {value[1]}"

        # endregion

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            settings = {}

            if contrast_switch.is_switched():
                contrast_min, contrast_max = contrast_slider.get_value()
                settings["contrast"] = {
                    "min": contrast_min,
                    "max": contrast_max,
                    "center_grey": center_grey_checkbox.is_checked()
                    if center_grey_checkbox.is_checked()
                    else False,
                }
            else:
                settings["contrast"] = {
                    "min": 1,
                    "max": 1,
                    "center_grey": False,
                }
            if brightness_switch.is_switched():
                brightness_min, brightness_max = brightness_slider.get_value()
                settings["brightness"] = {
                    "min": brightness_min,
                    "max": brightness_max,
                }
            else:
                settings["brightness"] = {
                    "min": 0,
                    "max": 0,
                }
            return settings

        def _update_preview():
            contrast_min, contrast_max = contrast_slider.get_value()
            contrast_preview_widget.set(
                text=f"min: {contrast_min} - max: {contrast_max}", status="text"
            )
            brightness_min, brightness_max = brightness_slider.get_value()
            brightness_preview_widget.set(
                text=f"min: {brightness_min} - max: {brightness_max}", status="text"
            )

        def _set_settings_from_json(settings: dict):
            # contrast_min_val, contrast_max_val = contrast_slider.get_value()
            if "contrast" in settings:
                contrast_min_val = settings["contrast"].get("min", 1)
                contrast_max_val = settings["contrast"].get("max", 1)
                center_grey_val = settings["contrast"].get("center_grey", False)
                if contrast_min_val != 1 or contrast_max_val != 1:
                    contrast_switch.on()
                    if center_grey_val is True:
                        center_grey_checkbox.check()
                    contrast_slider.show()
                    center_grey_checkbox.show()
                    contrast_preview_widget.show()
                else:
                    contrast_switch.off()
                    center_grey_checkbox.uncheck()
                    contrast_slider.hide()
                    center_grey_checkbox.hide()
                    contrast_preview_widget.hide()
                contrast_slider.set_value([contrast_min_val, contrast_max_val])

            # brightness_min_val, brightness_max_val = brightness_slider.get_value()
            if "brightness" in settings:
                brightness_min_val = settings["brightness"].get("min", 0)
                brightness_max_val = settings["brightness"].get("max", 0)
                if brightness_min_val != 0 or brightness_max_val != 0:
                    brightness_switch.on()
                    brightness_slider.show()
                    brightness_preview_widget.show()
                else:
                    brightness_switch.off()
                    brightness_slider.hide()
                    brightness_preview_widget.hide()
                brightness_slider.set_value([brightness_min_val, brightness_max_val])

            _update_preview()

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="contrast_container",
                    option_component=NodesFlow.WidgetOptionComponent(contrast_container),
                ),
                NodesFlow.Node.Option(
                    name="Center grey. Center colors of images (subtract 128) first",
                    option_component=NodesFlow.WidgetOptionComponent(center_grey_checkbox),
                ),
                NodesFlow.Node.Option(
                    name="contrast_preview",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=contrast_preview_widget,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="contrast_slider",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=contrast_slider,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="brightness_container",
                    option_component=NodesFlow.WidgetOptionComponent(brightness_container),
                ),
                NodesFlow.Node.Option(
                    name="brightness_preview",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=brightness_preview_widget,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="brightness_slider",
                    option_component=NodesFlow.WidgetOptionComponent(brightness_slider),
                ),
                NodesFlow.Node.Option(
                    name="brightness_slider",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=brightness_slider,
                    ),
                ),
            ]
            return {
                "src": [],
                "dst": [],
                "settings": settings_options,
            }

        return Layer(
            action=cls,
            id=layer_id,
            create_options=create_options,
            get_settings=get_settings,
        )
