from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import NodesFlow, Text, Grid, InputNumber

from src.ui.dtl import SpatialLevelAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs, get_text_font_size


class SlidingWindowAction(SpatialLevelAction):
    name = "sliding_window"
    title = "Sliding Window"
    docs_url = (
        "https://docs.supervisely.com/data-manipulation/index/transformation-layers/sliding_window"
    )
    description = "Crop part of image with its annotations with sliding window algorithms."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        window_text = Text("Window", status="text", font_size=get_text_font_size())
        width_text = Text("Width", status="text", font_size=get_text_font_size())
        height_text = Text("Height", status="text", font_size=get_text_font_size())
        width_input = InputNumber(value=128, step=1, controls=True)
        height_input = InputNumber(value=128, step=1, controls=True)
        window_settings = Grid([width_text, height_text, width_input, height_input], columns=2)

        min_overlap_text = Text("Min Overlap", status="text", font_size=get_text_font_size())
        x_text = Text("X", status="text", font_size=get_text_font_size())
        y_text = Text("Y", status="text", font_size=get_text_font_size())
        x_input = InputNumber(value=32, step=1, controls=True)
        y_input = InputNumber(value=32, step=1, controls=True)
        min_overlap_settings = Grid([x_text, y_text, x_input, y_input], columns=2)

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return {
                "window": {
                    "width": width_input.get_value(),
                    "height": height_input.get_value(),
                },
                "min_overlap": {
                    "x": x_input.get_value(),
                    "y": y_input.get_value(),
                },
            }

        def _set_settings_from_json(settings: dict):
            if "window" in settings:
                window = settings["window"]
                width_input.value = window["width"]
                height_input.value = window["height"]

            if "min_overlap" in settings:
                min_overlap = settings["min_overlap"]
                x_input.value = min_overlap["x"]
                y_input.value = min_overlap["y"]

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="window_text",
                    option_component=NodesFlow.WidgetOptionComponent(window_text),
                ),
                NodesFlow.Node.Option(
                    name="window_settings",
                    option_component=NodesFlow.WidgetOptionComponent(window_settings),
                ),
                NodesFlow.Node.Option(
                    name="min_overlap_text",
                    option_component=NodesFlow.WidgetOptionComponent(min_overlap_text),
                ),
                NodesFlow.Node.Option(
                    name="min_overlap_settings",
                    option_component=NodesFlow.WidgetOptionComponent(min_overlap_settings),
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
