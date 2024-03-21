import json
from typing import Optional
from os.path import realpath, dirname

from src.ui.dtl import OutputAction
from src.ui.dtl.Layer import Layer
from supervisely.app.widgets import NodesFlow, Text, Input, Checkbox, Markdown
from src.ui.dtl.utils import get_layer_docs, get_text_font_size
import src.globals as g


class ExportArchiveAction(OutputAction):
    name = "export_archive"
    legacy_name = "save"
    title = "Export Archive"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/save-layers/save"
    description = "Export annotations and images to Team Files."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None) -> Layer:
        save_path_text = Text("Archive name", status="text", font_size=get_text_font_size())
        save_path_input = Input(value="", placeholder="Enter archive name", size="small")
        visualize_checkbox = Checkbox("Visualize")
        if g.MODALITY_TYPE == "videos":
            visualize_checkbox.hide()

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return {
                "visualize": visualize_checkbox.is_checked(),
            }

        def get_dst(options_json: dict) -> dict:
            dst = save_path_input.get_value()
            if dst is None or dst == "":
                return []
                # raise ValueError("Destination is not specified")
            if dst[0] == "[":
                dst = json.loads(dst)
            else:
                dst = [dst.strip("'\"")]
            return dst

        def _set_settings_from_json(settings: dict):
            visualize_setting = settings.get("visualize", False)
            if visualize_setting:
                visualize_checkbox.check()
            else:
                visualize_checkbox.uncheck()

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="destination_text",
                    option_component=NodesFlow.WidgetOptionComponent(save_path_text),
                ),
                NodesFlow.Node.Option(
                    name="dst", option_component=NodesFlow.WidgetOptionComponent(save_path_input)
                ),
                NodesFlow.Node.Option(
                    name="Visualize",
                    option_component=NodesFlow.WidgetOptionComponent(visualize_checkbox),
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
            get_dst=get_dst,
            get_settings=get_settings,
            need_preview=False,
        )

    @classmethod
    def create_outputs(cls):
        return []
