from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import NodesFlow

from src.ui.dtl.Action import FilterAndConditionAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs


class FilterVideoWithoutAnnotation(FilterAndConditionAction):
    name = "filter_video_without_annotation"
    title = "Filter Videos without Annotations"
    docs_url = ""
    description = "Filter Videos without objects and tags."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        def get_settings(options_json: dict) -> dict:
            return {}

        def create_options(src: list, dst: list, settings: dict) -> dict:
            return {
                "src": [],
                "dst": [],
                "settings": [],
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
