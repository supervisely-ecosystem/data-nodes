from typing import Optional
import json
from os.path import realpath, dirname

from supervisely.app.widgets import NodesFlow, Text, Input

from src.ui.dtl import OutputAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs, get_text_font_size


class CreateNewProjectAction(OutputAction):
    name = "create_new_project"
    legacy_name = "supervisely"
    title = "Create New Project"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/save-layers/supervisely"
    description = "Save results of data transformations to a new project in current workspace."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None) -> Layer:
        sly_project_name_text = Text("Project name", status="text", font_size=get_text_font_size())
        sly_project_name_input = Input(value="", placeholder="Enter project name", size="small")

        def get_dst(options_json: dict) -> dict:
            dst = sly_project_name_input.get_value()
            if dst is None or dst == "":
                return []
            if dst[0] == "[":
                dst = json.loads(dst)
            else:
                dst = [dst.strip("'\"")]

            return dst

        def _set_settings_from_json(settings: dict):
            return

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="destination_text",
                    option_component=NodesFlow.WidgetOptionComponent(sly_project_name_text),
                ),
                NodesFlow.Node.Option(
                    name="dst",
                    option_component=NodesFlow.WidgetOptionComponent(sly_project_name_input),
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
            need_preview=False,
        )

    @classmethod
    def create_outputs(cls):
        return []
