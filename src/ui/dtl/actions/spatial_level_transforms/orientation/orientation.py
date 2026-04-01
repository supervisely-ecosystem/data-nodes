from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import NodesFlow, Select, Text

from src.ui.dtl import SpatialLevelAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs, get_text_font_size


class OrientationAction(SpatialLevelAction):
    name = "orientation"
    title = "Orientation"
    docs_url = "https://docs.supervisely.com/data-manipulation/index"
    description = "Rotate images to the target portrait or landscape orientation."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        target_orientation_text = Text(
            "Target orientation",
            status="text",
            font_size=get_text_font_size(),
        )
        target_orientation_selector = Select(
            items=[
                Select.Item("landscape", "Landscape"),
                Select.Item("portrait", "Portrait"),
            ],
            size="small",
        )

        rotation_direction_text = Text(
            "Rotation direction",
            status="text",
            font_size=get_text_font_size(),
        )
        rotation_direction_selector = Select(
            items=[
                Select.Item("clockwise", "Clockwise"),
                Select.Item("counter_clockwise", "Counter clockwise"),
            ],
            size="small",
        )

        def get_settings(options_json: dict) -> dict:
            return {
                "target_orientation": target_orientation_selector.get_value(),
                "rotation_direction": rotation_direction_selector.get_value(),
            }

        def _set_settings_from_json(settings: dict):
            target_orientation_selector.set_value(
                settings.get("target_orientation", "landscape")
            )
            rotation_direction_selector.set_value(
                settings.get("rotation_direction", "clockwise")
            )

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="target_orientation_text",
                    option_component=NodesFlow.WidgetOptionComponent(target_orientation_text),
                ),
                NodesFlow.Node.Option(
                    name="target_orientation",
                    option_component=NodesFlow.WidgetOptionComponent(
                        target_orientation_selector
                    ),
                ),
                NodesFlow.Node.Option(
                    name="rotation_direction_text",
                    option_component=NodesFlow.WidgetOptionComponent(rotation_direction_text),
                ),
                NodesFlow.Node.Option(
                    name="rotation_direction",
                    option_component=NodesFlow.WidgetOptionComponent(
                        rotation_direction_selector
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
