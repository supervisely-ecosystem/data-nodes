from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import NodesFlow, Container, Text, InputNumber, Select, Field

from src.ui.dtl.Action import FilterAndConditionAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import (
    get_layer_docs,
    get_text_font_size,
)


class FilterVideoByDuration(FilterAndConditionAction):
    name = "filter_video_by_duration"
    title = "Filter Videos by Duration"
    docs_url = ""
    description = "Filter Videos based on their duration."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        settings_edit_text = Text("Duration unit", status="text", font_size=get_text_font_size())
        measure_unit_selector_items = [
            Select.Item(value="frames", label="Frames"),
            Select.Item(value="seconds", label="Seconds"),
        ]
        duration_unit_selector = Select(measure_unit_selector_items, size="small")

        dur_thresh_input = InputNumber(value=500, step=1, controls=True, size="small")
        duration_settings = Field(
            title="Duration threshold",
            description=(
                "Videos with duration less than selected will be filtered out to the output branch 'True', "
                "rest of the videos will be filtered out to the output branch 'False'"
            ),
            content=dur_thresh_input,
        )

        settings_container = Container(
            widgets=[settings_edit_text, duration_unit_selector, duration_settings],
        )
        saved_settings = {}

        @dur_thresh_input.value_changed
        def dur_thresh_input_cb(value):
            _save_settings()

        @duration_unit_selector.value_changed
        def duration_unit_selector_cb(value):
            _save_settings()

        def _save_settings():
            nonlocal saved_settings
            settings = {
                "duration_unit": duration_unit_selector.get_value(),
                "duration_threshold": dur_thresh_input.get_value(),
            }
            saved_settings = settings

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return saved_settings

        def _set_settings_from_json(settings: dict):
            duration_unit = settings.get("duration_unit", "frames")
            duration_unit_selector.set_value(duration_unit)
            dur_thresh = settings.get("duration_threshold", 500)
            dur_thresh_input.value = dur_thresh
            _save_settings()

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="Settings",
                    option_component=NodesFlow.WidgetOptionComponent(settings_container),
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

    @classmethod
    def create_outputs(cls):
        return [
            NodesFlow.Node.Output("destination_true", "Output True"),
            NodesFlow.Node.Output("destination_false", "Output False"),
        ]
