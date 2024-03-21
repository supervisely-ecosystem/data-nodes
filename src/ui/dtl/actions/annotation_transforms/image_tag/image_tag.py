from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import NodesFlow, SelectTagMeta, Text, Select
from supervisely import ProjectMeta, TagMeta, Tag
from supervisely.annotation.tag_meta import TagValueType

from src.ui.dtl import AnnotationAction
from src.ui.dtl.Layer import Layer
from src.ui.widgets import InputTag
from src.ui.dtl.utils import (
    get_layer_docs,
    get_text_font_size,
)


class ImageTagAction(AnnotationAction):
    name = "image_tag"
    legacy_name = "tag"
    title = "Image Tag"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/transformation-layers/tag"
    description = "Add or remove tags from images."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        _current_meta = ProjectMeta()
        _empty_tag_meta = TagMeta(name="", value_type=TagValueType.NONE)

        input_tag = InputTag(_empty_tag_meta)

        input_tag_text = Text("Image Tag", status="text", font_size=get_text_font_size())
        select_tag_meta = SelectTagMeta(project_meta=_current_meta, size="small")

        action_text = Text("Action", status="text", font_size=get_text_font_size())
        action_selector = Select(
            [Select.Item("add", "Add to image"), Select.Item("delete", "Delete from image")],
            size="small",
        )

        @select_tag_meta.value_changed
        def select_tag_meta_value_changed(tag_meta: TagMeta):
            input_tag.loading = True
            if tag_meta is None:
                tag_meta = _empty_tag_meta
            input_tag.set_tag_meta(tag_meta)
            input_tag.loading = False

        def _get_tag():
            selected_tag = input_tag.get_tag()
            selected_tag: Tag
            if selected_tag is None:
                return None
            if selected_tag.meta == _empty_tag_meta:
                return None
            return {
                "name": selected_tag.meta.name,
                "value": selected_tag.value,
            }

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return {"tag": _get_tag(), "action": action_selector.get_value()}

        def _set_settings_from_json(settings: dict):
            tag = settings.get("tag", None)
            if tag is not None:
                select_tag_meta.loading = True
                input_tag.loading = True

                tag_name = settings["tag"]["name"]
                tag_value = settings["tag"]["value"]
                tag_meta = select_tag_meta.get_tag_meta_by_name(tag_name)
                select_tag_meta.set_name(tag_name)

                input_tag.set_tag_meta(tag_meta)
                input_tag.set_value(tag_value)

                select_tag_meta.loading = False
                input_tag.loading = False

            action = settings.get("action", None)
            if action is not None:
                action_selector.set_value(action)

        def data_changed_cb(**kwargs):
            project_meta = kwargs.get("project_meta", None)
            if project_meta is None:
                return
            nonlocal _current_meta, _empty_tag_meta
            if _current_meta == project_meta:
                return

            select_tag_meta.loading = True
            current_tag_meta = select_tag_meta.get_selected_item()
            current_tag_value = input_tag.get_value()

            select_tag_meta.set_project_meta(project_meta)

            tag_metas = [tm for tm in project_meta.tag_metas]
            if len(tag_metas) == 0:
                input_tag.set_tag_meta(_empty_tag_meta)
            elif current_tag_meta is not None and current_tag_meta.name in [
                tm.name for tm in tag_metas
            ]:
                # to preserve selected tag meta and value
                tag_meta = [tm for tm in tag_metas if tm.name == current_tag_meta.name][0]
                select_tag_meta.set_name(current_tag_meta.name)
                input_tag.set_tag_meta(tag_meta)
                input_tag.set_value(current_tag_value)
            else:
                select_tag_meta.set_name(tag_metas[0].name)
                input_tag.set_tag_meta(tag_metas[0])

            _current_meta = project_meta

            select_tag_meta.loading = False

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="input_tag_text",
                    option_component=NodesFlow.WidgetOptionComponent(widget=input_tag_text),
                ),
                NodesFlow.Node.Option(
                    name="Input Tag",
                    option_component=NodesFlow.WidgetOptionComponent(widget=select_tag_meta),
                ),
                NodesFlow.Node.Option(
                    name="input_tag_value",
                    option_component=NodesFlow.WidgetOptionComponent(widget=input_tag),
                ),
                NodesFlow.Node.Option(
                    name="action_text",
                    option_component=NodesFlow.WidgetOptionComponent(action_text),
                ),
                NodesFlow.Node.Option(
                    name="action_selector",
                    option_component=NodesFlow.WidgetOptionComponent(action_selector),
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
