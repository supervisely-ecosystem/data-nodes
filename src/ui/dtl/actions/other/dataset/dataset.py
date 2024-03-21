from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import NodesFlow, Text, Input, Checkbox

from src.ui.dtl import OtherAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs, get_text_font_size


class DatasetAction(OtherAction):
    name = "dataset"
    title = "Dataset"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/transformation-layers/dataset"
    description = "Places every image that it sees to dataset with a specified name."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        save_original_checkbox = Checkbox("Keep original datasets")

        ds_name_text = Text("Name", status="text", font_size=get_text_font_size())
        ds_name_input = Input(value="", placeholder="Enter dataset name", size="small")

        @save_original_checkbox.value_changed
        def save_original_checkbox_changed(is_checked: bool):
            if is_checked:
                ds_name_text.hide()
                ds_name_input.hide()
            else:
                ds_name_text.show()
                ds_name_input.show()

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            if save_original_checkbox.is_checked():
                return {
                    "rule": "save_original",
                }
            name = ds_name_input.get_value()
            name.strip("'\"").lstrip("'\"")
            return {
                "name": name,
            }

        def _set_settings_from_json(settings: dict):
            rule = settings.get("rule", None)
            if rule == "save_original":
                save_original_checkbox.check()
                ds_name_input.hide()
            else:
                save_original_checkbox.uncheck()
                ds_name = settings.get("name", "")
                ds_name_input.set_value(ds_name)
                ds_name_input.show()

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="Save original",
                    option_component=NodesFlow.WidgetOptionComponent(save_original_checkbox),
                ),
                NodesFlow.Node.Option(
                    name="name_text", option_component=NodesFlow.WidgetOptionComponent(ds_name_text)
                ),
                NodesFlow.Node.Option(
                    name="name", option_component=NodesFlow.WidgetOptionComponent(ds_name_input)
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
