from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import (
    NodesFlow,
    Text,
    Select,
    NotificationBox,
    Container,
)
from supervisely import ProjectMeta

from src.ui.dtl import FilterAndConditionAction
from src.ui.dtl.Layer import Layer
from src.ui.widgets import InputTagList
from src.ui.dtl.utils import (
    get_layer_docs,
    get_text_font_size,
)


class FilterVideosByTag(FilterAndConditionAction):
    name = "filter_videos_by_tag"
    title = "Filter Videos by Tags"
    docs_url = ""
    description = "Filter Videos based on the presence of specified tags."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        _current_meta = ProjectMeta()

        condition_text = Text("Condition", status="text", font_size=get_text_font_size())
        condition_selector = Select(
            [
                Select.Item("with", "Video has tags"),
                Select.Item("without", "Video doesn't have tags"),
            ],
            size="small",
        )

        input_tag_text = Text("Select Tags", status="text", font_size=get_text_font_size())
        no_tags_notification = NotificationBox(
            title="No tags in project meta",
            description="Connect the node and ensure there are tags in source project meta",
        )
        no_tags_notification.show()
        input_tag_list = InputTagList(tag_metas=[], multiple=True, max_width=316)
        input_tag_list.hide()
        input_tag_list_container = Container(widgets=[input_tag_list, no_tags_notification], gap=0)

        def _get_tags():
            selected_tags = input_tag_list.get_selected_tags()
            return [
                {
                    "name": tag.meta.name,
                    "value": tag.value,
                }
                for tag in selected_tags
            ]

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return {"tags": _get_tags(), "condition": condition_selector.get_value()}

        def _set_settings_from_json(settings: dict):
            tags = settings.get("tags", [])

            input_tag_list.select(tag["name"] for tag in tags)
            input_tag_list.set_values({tag["name"]: tag["value"] for tag in tags})

            condition = settings.get("condition", None)
            if condition is not None:
                condition_selector.set_value(condition)

        def data_changed_cb(**kwargs):
            project_meta = kwargs.get("project_meta", None)
            if project_meta is None:
                return
            nonlocal _current_meta
            if _current_meta == project_meta:
                return

            input_tag_list.loading = True
            current_tags = input_tag_list.get_all_tags()
            selected_tag_metas = input_tag_list.get_selected_tag_metas()

            tag_metas = project_meta.tag_metas
            input_tag_list.set(tag_metas)

            # to preserve current settings
            input_tag_list.set_values({tag.meta.name: tag.value for tag in current_tags})
            input_tag_list.deselect_all()
            input_tag_list.select([tm.name for tm in selected_tag_metas])

            if len(tag_metas) == 0:
                no_tags_notification.show()
                input_tag_list.hide()
            else:
                no_tags_notification.hide()
                input_tag_list.show()

            _current_meta = project_meta

            input_tag_list.loading = False

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="condition_text",
                    option_component=NodesFlow.WidgetOptionComponent(condition_text),
                ),
                NodesFlow.Node.Option(
                    name="condition_selector",
                    option_component=NodesFlow.WidgetOptionComponent(condition_selector),
                ),
                NodesFlow.Node.Option(
                    name="input_tag_text",
                    option_component=NodesFlow.WidgetOptionComponent(widget=input_tag_text),
                ),
                NodesFlow.Node.Option(
                    "test_tag_list",
                    option_component=NodesFlow.WidgetOptionComponent(input_tag_list_container),
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
            data_changed_cb=data_changed_cb,
            need_preview=False,
        )

    @classmethod
    def create_outputs(cls):
        return [
            NodesFlow.Node.Output("destination_true", "Output True"),
            NodesFlow.Node.Output("destination_false", "Output False"),
        ]
