from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import NodesFlow, Text, Slider

from src.ui.dtl import PixelLevelAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs, get_slider_style, get_text_font_size


class RandomColorsAction(PixelLevelAction):
    name = "random_color"
    title = "Random Color"
    docs_url = (
        "https://docs.supervisely.com/data-manipulation/index/transformation-layers/random_color"
    )
    description = "Change image colors by randomly moving each of RGB components."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        color_strength_text = Text("Strength", status="text", font_size=get_text_font_size())
        color_strength_slider = Slider(
            value=0.50,
            min=0,
            max=1,
            step=0.01,
            show_input=True,
            show_input_controls=True,
            style=get_slider_style(),
        )

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return {
                "strength": color_strength_slider.get_value(),
            }

        def _set_settings_from_json(settings: dict):
            strength = settings.get("strength", 0.50)
            if strength is not None:
                color_strength_slider.set_value(strength)

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="strength_text",
                    option_component=NodesFlow.WidgetOptionComponent(color_strength_text),
                ),
                NodesFlow.Node.Option(
                    name="strength",
                    option_component=NodesFlow.WidgetOptionComponent(color_strength_slider),
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
