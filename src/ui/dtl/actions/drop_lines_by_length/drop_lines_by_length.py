import copy
from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import NodesFlow, Button, Container, Flexbox, Text
from supervisely import ProjectMeta, Polyline, AnyGeometry

from src.ui.dtl import AnnotationAction
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
    create_save_btn
)
import src.globals as g


class DropLinesByLengthAction(AnnotationAction):
    name = "drop_lines_by_length"
    title = "Drop Lines by Length"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/transformation-layers/drop_lines_by_length"
    description = "Removes too long or to short lines."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        _current_meta = ProjectMeta()
        classes_list_widget = ClassesList(multiple=True)
        classes_list_preview = ClassesListPreview()
        classes_list_save_btn = create_save_btn()
        classes_list_set_default_btn = Button("Set Default", icon="zmdi zmdi-refresh")
        classes_list_widgets_container = Container(
            widgets=[
                classes_list_widget,
                Flexbox(
                    widgets=[
                        classes_list_save_btn,
                        classes_list_set_default_btn,
                    ],
                    gap=105,
                ),
            ]
        )
        classes_list_edit_text = Text("Classes List")
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

        saved_classes_settings = []
        default_classes_settings = []

        def _get_classes_list_value():
            return get_classes_list_value(classes_list_widget, multiple=True)

        def _set_classes_list_preview():
            set_classes_list_preview(
                classes_list_widget, classes_list_preview, saved_classes_settings
            )

        def _save_classes_list_settings():
            nonlocal saved_classes_settings
            saved_classes_settings = _get_classes_list_value()

        def _set_default_classes_mapping_setting():
            # save setting to var
            nonlocal saved_classes_settings
            saved_classes_settings = copy.deepcopy(default_classes_settings)

        def meta_changed_cb(project_meta: ProjectMeta):
            nonlocal _current_meta
            if project_meta == _current_meta:
                return
            _current_meta = project_meta
            classes_list_widget.loading = True
            obj_classes = [
                cls
                for cls in project_meta.obj_classes
                if cls.geometry_type in [Polyline, AnyGeometry]
            ]

            # set classes to widget
            classes_list_widget.set(obj_classes)

            # update settings according to new meta
            nonlocal saved_classes_settings
            saved_classes_settings = classes_list_settings_changed_meta(
                saved_classes_settings, obj_classes
            )

            # update settings preview
            _set_classes_list_preview()

            classes_list_widget.loading = False

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            settins = {
                "lines_classes": saved_classes_settings,
                "resolution_compensation": bool(options_json["Resolution Compensation"]),
                "invert": bool(options_json["Invert"]),
            }
            if options_json["Min Length"]:
                settins["min_length"] = options_json["min_length"]
            if options_json["Max Length"]:
                settins["max_length"] = options_json["max_length"]
            return settins

        def _set_settings_from_json(settings: dict):
            classes_list_widget.loading = True
            classes_list_settings = settings.get("lines_classes", [])
            set_classes_list_settings_from_json(
                classes_list_widget=classes_list_widget, settings=classes_list_settings
            )
            # save settings
            _save_classes_list_settings()
            # update settings preview
            _set_classes_list_preview()
            classes_list_widget.loading = False

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

            min_length_flag = False
            min_length_val = 1
            if "min_length" in settings:
                min_length_flag = True
                min_length_val = settings.get("min_length", 1)
            max_length_flag = False
            max_length_val = 1
            if "max_length" in settings:
                max_length_flag = True
                max_length_val = settings.get("max_length", 1)
            invert_val = settings.get("invert", False)
            resolution_compensation_val = settings.get("resolution_compensation", False)

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
                    name="Resolution Compensation",
                    option_component=NodesFlow.CheckboxOptionComponent(
                        default_value=resolution_compensation_val
                    ),
                ),
                NodesFlow.Node.Option(
                    name="Invert",
                    option_component=NodesFlow.CheckboxOptionComponent(default_value=invert_val),
                ),
                NodesFlow.Node.Option(
                    name="Min Length",
                    option_component=NodesFlow.CheckboxOptionComponent(min_length_flag),
                ),
                NodesFlow.Node.Option(
                    name="min_length",
                    option_component=NodesFlow.IntegerOptionComponent(
                        min=0, default_value=min_length_val
                    ),
                ),
                NodesFlow.Node.Option(
                    name="Max Length",
                    option_component=NodesFlow.CheckboxOptionComponent(max_length_flag),
                ),
                NodesFlow.Node.Option(
                    name="max_length",
                    option_component=NodesFlow.IntegerOptionComponent(
                        min=0, default_value=max_length_val
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
            meta_changed_cb=meta_changed_cb,
        )
