from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import NodesFlow, Select, Text

from src.ui.dtl import SpatialLevelAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs, get_text_font_size


class FlipAction(SpatialLevelAction):
    name = "flip"
    title = "Flip"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/transformation-layers/flip"
    description = "Flips data (image + annotation) vertically or horizontally."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        axis_text = Text("Axis", status="text", font_size=get_text_font_size())
        axis_selector_items = [
            Select.Item("vertical", "Vertical"),
            Select.Item("horizontal", "Horizontal"),
        ]
        axis_selector = Select(items=axis_selector_items, size="small")

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return {
                "axis": axis_selector.get_value(),
            }

        def _set_settings_from_json(settings: dict):
            axis = settings.get("axis", "vertical")
            axis_selector.set_value(axis)

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="axis_text",
                    option_component=NodesFlow.WidgetOptionComponent(axis_text),
                ),
                NodesFlow.Node.Option(
                    name="axis_selector",
                    option_component=NodesFlow.WidgetOptionComponent(axis_selector),
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
