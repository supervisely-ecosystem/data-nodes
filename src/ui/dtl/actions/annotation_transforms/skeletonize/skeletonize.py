import copy
from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import NodesFlow, Button, Container, Flexbox, Text, Select, Field
from supervisely import ProjectMeta, Bitmap, AnyGeometry

from src.ui.dtl.Action import AnnotationAction
from src.ui.dtl.Layer import Layer
from src.ui.widgets import ClassesList, ClassesListPreview
from src.ui.dtl.utils import (
    classes_list_settings_changed_meta,
    get_classes_list_value,
    set_classes_list_preview,
    set_classes_list_settings_from_json,
    get_set_settings_button_style,
    get_set_settings_container,
    get_layer_docs,
    create_save_btn,
    create_set_default_btn,
    get_text_font_size,
)
import src.globals as g


class SkeletonizeAction(AnnotationAction):
    name = "skeletonize"
    title = "Skeletonize"
    docs_url = (
        "https://docs.supervisely.com/data-manipulation/index/transformation-layers/skeletonize"
    )
    description = "Extracts skeletons from Bitmap."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None) -> Layer:
        _current_meta = ProjectMeta()
        classes_list_widget = ClassesList(multiple=True)
        classes_list_preview = ClassesListPreview()
        classes_list_save_btn = create_save_btn()
        classes_list_set_default_btn = create_set_default_btn()
        classes_list_widget_field = Field(
            content=classes_list_widget,
            title="Classes",
            description="Select classes for which you want to extract skeletons",
        )
        classes_list_widgets_container = Container(
            widgets=[
                classes_list_widget_field,
                Flexbox(
                    widgets=[
                        classes_list_save_btn,
                        classes_list_set_default_btn,
                    ],
                    gap=110,
                ),
            ]
        )
        classes_list_edit_text = Text("Classes", status="text", font_size=get_text_font_size())
        classes_list_edit_btn = Button(
            text="EDIT",
            icon="zmdi zmdi-edit",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )
        classes_list_edit_container = get_set_settings_container(
            classes_list_edit_text, classes_list_edit_btn
        )

        skeletonize_methods_text = Text(
            "Operation type", status="text", font_size=get_text_font_size()
        )
        skeletonize_methods_selector = Select(
            [
                Select.Item("skeletonization", "Skeletonization"),
                Select.Item("medial_axis", "Medial axis"),
                Select.Item("thinning", "Thinning"),
            ],
            size="small",
        )

        saved_classes_settings = "default"
        default_classes_settings = "default"

        def _get_classes_list_value():
            return get_classes_list_value(classes_list_widget, multiple=True)

        def _set_classes_list_preview():
            set_classes_list_preview(
                classes_list_widget,
                classes_list_preview,
                saved_classes_settings,
                classes_list_edit_text,
            )

        def _save_classes_list_settings():
            nonlocal saved_classes_settings
            saved_classes_settings = _get_classes_list_value()

        def _set_default_classes_mapping_setting():
            # save setting to var
            nonlocal saved_classes_settings
            saved_classes_settings = copy.deepcopy(default_classes_settings)

        def data_changed_cb(**kwargs):
            project_meta = kwargs.get("project_meta", None)
            if project_meta is None:
                return
            nonlocal _current_meta
            if project_meta == _current_meta:
                return
            _current_meta = project_meta

            classes_list_widget.loading = True
            obj_classes = [
                cls
                for cls in project_meta.obj_classes
                if cls.geometry_type in [Bitmap, AnyGeometry]
            ]

            # set classes to widget
            classes_list_widget.set(obj_classes)

            # update settings according to new meta
            nonlocal saved_classes_settings
            saved_classes_settings = classes_list_settings_changed_meta(
                saved_classes_settings, obj_classes
            )

            classes_names = saved_classes_settings
            if classes_names == "default":
                classes_names = [cls.name for cls in obj_classes]
            classes_list_widget.select(classes_names)

            # update settings preview
            _set_classes_list_preview()

            classes_list_widget.loading = False

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            classes = saved_classes_settings
            if saved_classes_settings == "default":
                classes = _get_classes_list_value()
            return {
                "classes": classes,
                "method": skeletonize_methods_selector.get_value(),
            }

        def _set_settings_from_json(settings: dict):
            classes_list_widget.loading = True
            classes_list_settings = settings.get("classes", default_classes_settings)
            set_classes_list_settings_from_json(
                classes_list_widget=classes_list_widget, settings=classes_list_settings
            )
            # save settings
            if classes_list_settings != "default":
                _save_classes_list_settings()
            # update settings preview
            _set_classes_list_preview()
            classes_list_widget.loading = False

            method = settings.get("method", None)
            if method is not None:
                skeletonize_methods_selector.set_value(method)

        @classes_list_save_btn.click
        def classes_list_save_btn_cb():
            _save_classes_list_settings()
            _set_classes_list_preview()
            g.updater("metas")

        @classes_list_set_default_btn.click
        def classes_list_set_default_btn_cb():
            _set_default_classes_mapping_setting()
            set_classes_list_settings_from_json(
                classes_list_widget=classes_list_widget, settings=saved_classes_settings
            )
            _set_classes_list_preview()
            g.updater("metas")

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            method_val = settings.get("method", "skeletonization")
            settings_options = [
                NodesFlow.Node.Option(
                    name="Select Classes",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=classes_list_edit_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(
                            classes_list_widgets_container
                        ),
                        sidebar_width=380,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="classes_preview_text",
                    option_component=NodesFlow.WidgetOptionComponent(classes_list_preview),
                ),
                NodesFlow.Node.Option(
                    name="skeletonize_methods_text",
                    option_component=NodesFlow.WidgetOptionComponent(skeletonize_methods_text),
                ),
                NodesFlow.Node.Option(
                    name="skeletonize_methods_selector",
                    option_component=NodesFlow.WidgetOptionComponent(skeletonize_methods_selector),
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
        )
