from typing import Optional
from os.path import realpath, dirname
from math import ceil
from supervisely.app.widgets import NodesFlow, InputNumber, Text, Checkbox

from src.ui.dtl import SpatialLevelAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs, get_text_font_size

# DEFAULT_ASPECT_RATIO = 16 / 9


class ResizeAction(SpatialLevelAction):
    name = "resize"
    title = "Resize"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/transformation-layers/resize"
    description = "Resize data (image + annotation) to the certain size."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        width_text = Text("Width", status="text", font_size=get_text_font_size())
        width_input = InputNumber(value=512, min=1, step=1, controls=True)

        height_text = Text("Height", status="text", font_size=get_text_font_size())
        height_input = InputNumber(value=512, min=1, step=1, controls=True)

        # scale_proportionally_checkbox = Checkbox("Scale proportionally")
        keep_aspect_ratio_checkbox = Checkbox("Keep aspect ratio")

        # @height_input.value_changed
        # def height_input_value_changed(value):
        #     if scale_proportionally_checkbox.is_checked():
        #         width_input.value = int(ceil(value / DEFAULT_ASPECT_RATIO))

        # @width_input.value_changed
        # def width_input_value_changed(value):
        #     if scale_proportionally_checkbox.is_checked():
        #         height_input.value = int(ceil((value * DEFAULT_ASPECT_RATIO)))

        # @scale_proportionally_checkbox.value_changed
        # def scale_proportionally_checkbox_value_changed(is_checked):
        #     if is_checked:
        #         height_input.disable()
        #         width = width_input.get_value()
        #         height_input.value = int(ceil((width / DEFAULT_ASPECT_RATIO)))
        #     else:
        #         height_input.enable()

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            keep_aspect_ratio = keep_aspect_ratio_checkbox.is_checked()
            width = width_input.get_value()
            height = height_input.get_value()
            if width * height == 0:
                raise ValueError("Width and Height must be positive")
            if not keep_aspect_ratio:
                if width == -1:
                    raise ValueError(
                        "Width = -1 is not allowed when Keep aspect ratio is not enabled"
                    )
                if height == -1:
                    raise ValueError(
                        "Height = -1 is not allowed when Keep aspect ratio is not enabled"
                    )
            return {
                "width": width,
                "height": height,
                "aspect_ratio": {
                    "keep": keep_aspect_ratio,
                },
            }

        def _set_settings_from_json(settings: dict):
            width = settings.get("width", 512)
            height = settings.get("height", 512)
            if "aspect_ratio" in settings:
                keep_aspect_ratio: dict = settings["aspect_ratio"].get("keep", False)
            else:
                keep_aspect_ratio = False

            width_input.value = width
            height_input.value = height
            if keep_aspect_ratio:
                keep_aspect_ratio_checkbox.check()
            else:
                keep_aspect_ratio_checkbox.uncheck()

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="width_text",
                    option_component=NodesFlow.WidgetOptionComponent(width_text),
                ),
                NodesFlow.Node.Option(
                    name="width_input",
                    option_component=NodesFlow.WidgetOptionComponent(width_input),
                ),
                NodesFlow.Node.Option(
                    name="height_text",
                    option_component=NodesFlow.WidgetOptionComponent(height_text),
                ),
                NodesFlow.Node.Option(
                    name="height_input",
                    option_component=NodesFlow.WidgetOptionComponent(height_input),
                ),
                # NodesFlow.Node.Option(
                #     name="scale_proportionally_checkbox",
                #     option_component=NodesFlow.WidgetOptionComponent(scale_proportionally_checkbox),
                # ),
                NodesFlow.Node.Option(
                    name="keep_aspect_ratio_checkbox",
                    option_component=NodesFlow.WidgetOptionComponent(keep_aspect_ratio_checkbox),
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
