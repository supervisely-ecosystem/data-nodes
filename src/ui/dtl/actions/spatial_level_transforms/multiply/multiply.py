from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import NodesFlow, InputNumber, Text

from src.ui.dtl import SpatialLevelAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs, get_text_font_size


class MultiplyAction(SpatialLevelAction):
    name = "multiply"
    title = "Multiply"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/transformation-layers/multiply"
    description = "Duplicates data (image + annotation)."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        multiply_text = Text("Multiply number", status="text", font_size=get_text_font_size())
        multiply_input = InputNumber(value=12, step=1, controls=True)

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return {
                "multiply": multiply_input.get_value(),
            }

        def _set_settings_from_json(settings: dict):
            multiply_cal = settings.get("multiply", 12)
            multiply_input.value = multiply_cal

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="multiply_text",
                    option_component=NodesFlow.WidgetOptionComponent(multiply_text),
                ),
                NodesFlow.Node.Option(
                    name="multiply_input",
                    option_component=NodesFlow.WidgetOptionComponent(multiply_input),
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
            need_preview=False,
        )
