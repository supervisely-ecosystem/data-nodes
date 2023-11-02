from typing import Optional
from os.path import realpath, dirname

from supervisely import ProjectMeta
from supervisely.app.widgets import (
    NodesFlow,
    Select,
    Container,
    Field,
    OneOf,
    Button,
    Text,
    SelectTagMeta,
)

from src.ui.dtl import AnnotationAction
from src.ui.dtl.Layer import Layer
from src.ui.widgets import ClassesList, ClassesListPreview, TagMetasPreview
from src.ui.dtl.utils import (
    get_set_settings_button_style,
    get_set_settings_container,
    get_layer_docs,
    create_save_btn,
    get_text_font_size,
)


class ImagesFilterAction(AnnotationAction):
    name = "images_filter"
    title = "Images Filter"
    docs_url = ""
    description = "Filter images by selected tags or classes."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        _current_meta = ProjectMeta()
        classes_selector = ClassesList(multiple=True)
        classes_field = Field(
            title="Classes",
            content=classes_selector,
            description=(
                "Select which classes must be present on the image. "
                "If no classes are selected, "
                "all images without classes be filtered out"
            ),
        )

        tags_selector = SelectTagMeta(
            project_meta=ProjectMeta(), multiselect=True, show_label=False, size="small"
        )
        tags_field = Field(
            title="Tags",
            content=tags_selector,
            description=(
                "Select which tags must be present on the image. "
                "If no tags are selected, "
                "all images without tags be filtered out"
            ),
        )

        filter_items = [
            Select.Item("classes", "Classes", classes_field),
            Select.Item("tags", "Tags", tags_field),
        ]
        filter_by_select = Select(filter_items, size="small")
        filter_by_inputs = OneOf(filter_by_select)

        filter_by_preview_text = Text("", status="text", font_size=get_text_font_size())
        filter_preview_classes_text = Text(
            "Include Classes", status="text", font_size=get_text_font_size()
        )
        classes_preview = ClassesListPreview()

        filter_preview_tags_text = Text(
            "Include Tags", status="text", font_size=get_text_font_size()
        )
        tags_preview = TagMetasPreview()

        filter_by_classes_preview_container = Container(
            widgets=[filter_by_preview_text, filter_preview_classes_text, classes_preview], gap=1
        )

        filter_by_tags_preview_container = Container(
            widgets=[filter_by_preview_text, filter_preview_tags_text, tags_preview], gap=1
        )

        _settings_preview_select = Select(
            items=[
                Select.Item("classes", "Included Classes", filter_by_classes_preview_container),
                Select.Item("tags", "Included Tags", filter_by_tags_preview_container),
            ],
            size="small",
        )
        settings_preview = OneOf(_settings_preview_select)
        settings_edit_text = Text("Settings", status="text", font_size=get_text_font_size())
        settings_edit_btn = Button(
            text="EDIT",
            icon="zmdi zmdi-edit",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )
        settings_edit_container = get_set_settings_container(settings_edit_text, settings_edit_btn)

        settings_save_btn = create_save_btn()
        settings_widgets_container = Container(
            widgets=[
                Field(title="Filter by", content=filter_by_select),
                filter_by_inputs,
                settings_save_btn,
            ]
        )

        saved_settings = {}

        def _set_tags_preview():
            names = _get_tags_value()
            tags_selector.set([tags_selector.get_tag_meta_by_name(name) for name in names])

        def _get_tags_value():
            return [name for name in tags_selector.get_selected_names() if name]

        def _set_preview():
            nonlocal saved_settings
            if "filter_by" not in saved_settings:
                return
            filter_by = saved_settings["filter_by"]
            if "classes" in filter_by:
                _settings_preview_select.set_value("classes")
                classes = saved_settings["filter_by"]["classes"]
                obj_classes = [cls for cls in classes.get_all_classes() if cls.name in classes]
                classes_preview.set(obj_classes)
            else:
                _set_tags_preview()

        def _save_settings():
            nonlocal saved_settings
            settings = {}
            filter_by = filter_by_select.get_value()
            if filter_by == "names":
                settings["filter_by"] = {
                    "names": [cls.name for cls in classes_selector.get_selected_classes()],
                }
                saved_settings = settings
            else:
                # settings["filter_by"] = {
                #     "polygon_sizes": {
                #         "filtering_classes": [cls.name for cls in classes.get_selected_classes()],
                #         "action": action_select.get_value(),
                #         "comparator": comparator_select.get_value(),
                #     },
                # }

                saved_settings = settings
            _set_preview()

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return saved_settings

        def _set_settings_from_json(settings: dict):
            if "filter_by" not in settings:
                return
            if "names" in settings["filter_by"]:
                classes_selector.loading = True
                filter_by_select.loading = True
                filter_by_select.set_value("names")
                classes_selector.select(settings["filter_by"]["names"])
                filter_by_select.loading = False
                classes_selector.loading = False
            else:
                filter_by_select.loading = True
                classes_selector.loading = True

                if "percent" in settings["filter_by"]["polygon_sizes"]["area_size"]:
                    filter_by_select.set_value("area_percent")

                else:
                    filter_by_select.set_value("bbox_size")

                classes_selector.select(settings["filter_by"]["polygon_sizes"]["filtering_classes"])

                filter_by_select.loading = False

                classes_selector.loading = False

            _save_settings()

        def meta_changed_cb(project_meta: ProjectMeta):
            nonlocal _current_meta
            if project_meta == _current_meta:
                return
            _current_meta = project_meta
            classes_selector.loading = True
            classes_selector.set(project_meta.obj_classes)
            _save_settings()
            classes_selector.loading = False

        settings_save_btn.click(_save_settings)

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="Set Filter",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=settings_edit_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(
                            settings_widgets_container
                        ),
                        sidebar_width=300,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="settings_preview",
                    option_component=NodesFlow.WidgetOptionComponent(settings_preview),
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
            meta_changed_cb=meta_changed_cb,
        )
