import copy
from os.path import realpath, dirname
from typing import Optional

from supervisely.app.widgets import NodesFlow, Button, Container, Flexbox, Text, Select, Field
from supervisely import ProjectMeta
from supervisely import Bitmap, AnyGeometry

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
    create_save_btn,
    create_set_default_btn,
    get_text_font_size,
)
from src.exceptions import BadSettingsError
import src.globals as g


class BitwiseMasksAction(AnnotationAction):
    name = "bitwise_masks"
    title = "Bitwise Masks"
    docs_url = (
        "https://docs.supervisely.com/data-manipulation/index/transformation-layers/bitwise_masks"
    )
    description = "Make bitwise operations between bitmap annotations."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        operation_type_text = Text("Operation type", status="text", font_size=get_text_font_size())
        operation_type_selector = Select(
            [Select.Item("nor", "nor"), Select.Item("and", "and"), Select.Item("or", "or")],
            size="small",
        )

        _current_meta = ProjectMeta()
        class_mask_widget = ClassesList()
        classes_to_correct_widget = ClassesList(multiple=True)
        classes_mask_widget_field = Field(
            content=class_mask_widget,
            title="Class",
            description="Choose the class that will be the basis for the mask's correction",
        )
        classes_to_correct_widget_field = Field(
            content=classes_to_correct_widget,
            title="Classes",
            description="Select which classes you want to have their masks corrected",
        )
        class_mask_preview = ClassesListPreview()
        classes_to_correct_preview = ClassesListPreview()

        save_class_mask_btn = create_save_btn()
        save_classes_to_correct_btn = create_save_btn()

        set_default_class_mask_btn = create_set_default_btn()
        set_default_classes_to_correct_btn = create_set_default_btn()

        class_mask_widgets_container = Container(
            widgets=[
                classes_mask_widget_field,
                Flexbox(
                    widgets=[
                        save_class_mask_btn,
                        set_default_class_mask_btn,
                    ],
                    gap=110,
                ),
            ]
        )
        classes_to_correct_widgets_container = Container(
            widgets=[
                classes_to_correct_widget_field,
                Flexbox(
                    widgets=[
                        save_classes_to_correct_btn,
                        set_default_classes_to_correct_btn,
                    ],
                    gap=105,
                ),
            ]
        )
        class_mask_edit_text = Text(
            "Class Mask",
            status="text",
            font_size=get_text_font_size(),
        )
        class_mask_edit_btn = Button(
            text="EDIT",
            icon="zmdi zmdi-edit",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )
        class_mask_edit_container = get_set_settings_container(
            class_mask_edit_text, class_mask_edit_btn
        )
        classes_to_correct_edit_text = Text(
            "Classes to correct", status="text", font_size=get_text_font_size()
        )
        classes_to_correct_edit_btn = Button(
            text="EDIT",
            icon="zmdi zmdi-edit",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )
        classes_to_correct_edit_container = get_set_settings_container(
            classes_to_correct_edit_text, classes_to_correct_edit_btn
        )

        saved_class_mask_settings = ""
        saved_classes_to_correct_settings = []

        default_class_mask_settings = ""
        default_classes_to_correct_settings = []

        def _get_class_mask_value():
            return get_classes_list_value(class_mask_widget, multiple=False)

        def _set_class_mask_preview():
            set_classes_list_preview(
                class_mask_widget,
                class_mask_preview,
                saved_class_mask_settings,
            )

        def _save_class_mask_settings():
            nonlocal saved_class_mask_settings
            saved_class_mask_settings = _get_class_mask_value()

        def _set_default_class_mask_setting():
            # save setting to var
            nonlocal saved_class_mask_settings
            saved_class_mask_settings = copy.deepcopy(default_class_mask_settings)

        def _get_classes_to_correct_value():
            return get_classes_list_value(classes_to_correct_widget, multiple=True)

        def _set_classes_to_correct_preview():
            set_classes_list_preview(
                classes_to_correct_widget,
                classes_to_correct_preview,
                saved_classes_to_correct_settings,
                classes_to_correct_edit_text,
            )

        def _save_classes_to_correct_settings():
            nonlocal saved_classes_to_correct_settings
            saved_classes_to_correct_settings = _get_classes_to_correct_value()

        def _set_default_classes_to_correct_setting():
            # save setting to var
            nonlocal saved_classes_to_correct_settings
            saved_classes_to_correct_settings = copy.deepcopy(default_classes_to_correct_settings)

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return {
                "type": operation_type_selector.get_value(),
                "class_mask": saved_class_mask_settings,
                "classes_to_correct": saved_classes_to_correct_settings,
            }

        def data_changed_cb(**kwargs):
            project_meta = kwargs.get("project_meta", None)
            if project_meta is None:
                return
            nonlocal _current_meta
            if project_meta == _current_meta:
                return
            _current_meta = project_meta

            class_mask_widget.loading = True
            obj_classes = [
                obj_class
                for obj_class in project_meta.obj_classes
                if obj_class.geometry_type in [Bitmap, AnyGeometry]
            ]
            # set classes to widget
            class_mask_widget.set(obj_classes)
            # update settings according to new meta
            nonlocal saved_class_mask_settings
            saved_class_mask_settings = classes_list_settings_changed_meta(
                saved_class_mask_settings, obj_classes
            )
            # update settings preview
            _set_class_mask_preview()
            class_mask_widget.loading = False

            classes_to_correct_widget.loading = True
            obj_classes = [
                obj_class
                for obj_class in project_meta.obj_classes
                if obj_class.geometry_type in [Bitmap, AnyGeometry]
            ]
            # set classes to widget
            classes_to_correct_widget.set(obj_classes)
            # update settings according to new meta
            nonlocal saved_classes_to_correct_settings
            saved_classes_to_correct_settings = classes_list_settings_changed_meta(
                saved_classes_to_correct_settings, obj_classes
            )
            # update settings preview
            _set_classes_to_correct_preview()
            classes_to_correct_widget.loading = False

        def _set_settings_from_json(settings):
            op_type = settings.get("type", None)
            if op_type is not None:
                operation_type_selector.set_value(op_type)

            class_mask_widget.loading = True
            classes_list_settings = settings.get("class_mask", "")
            set_classes_list_settings_from_json(
                classes_list_widget=class_mask_widget, settings=classes_list_settings
            )
            # save settings
            _save_class_mask_settings()
            # update settings preview
            _set_class_mask_preview()

            # exclude selected class from classes_to_correct_widget
            obj_classes = [
                obj_class
                for obj_class in _current_meta.obj_classes
                if obj_class.geometry_type in [Bitmap, AnyGeometry]
            ]
            classes_to_correct_widget.set(
                [cls for cls in obj_classes if cls.name != saved_class_mask_settings]
            )
            _save_classes_to_correct_settings()
            _set_classes_to_correct_preview()

            class_mask_widget.loading = False

            classes_to_correct_widget.loading = True
            classes_list_settings = settings.get("classes_to_correct", [])
            set_classes_list_settings_from_json(
                classes_list_widget=classes_to_correct_widget, settings=classes_list_settings
            )
            # save settings
            _save_classes_to_correct_settings()
            # update settings preview
            _set_classes_to_correct_preview()
            classes_to_correct_widget.loading = False

        @save_class_mask_btn.click
        def save_class_mask_btn_cb():
            _save_class_mask_settings()
            _set_class_mask_preview()

            # exclude selected class from classes_to_correct_widget
            obj_classes = [
                obj_class
                for obj_class in _current_meta.obj_classes
                if obj_class.geometry_type in [Bitmap, AnyGeometry]
            ]
            classes_to_correct_widget.set(
                [cls for cls in obj_classes if cls.name != saved_class_mask_settings]
            )
            _save_classes_to_correct_settings()
            _set_classes_to_correct_preview()

            g.updater("metas")

        @set_default_class_mask_btn.click
        def set_default_class_mask_btn_cb():
            _set_default_class_mask_setting()
            set_classes_list_settings_from_json(
                classes_list_widget=class_mask_widget, settings=saved_class_mask_settings
            )
            _set_class_mask_preview()
            g.updater("metas")

        @save_classes_to_correct_btn.click
        def save_classes_to_correct_btn_cb():
            _save_classes_to_correct_settings()
            _set_classes_to_correct_preview()
            g.updater("metas")

        @set_default_classes_to_correct_btn.click
        def set_default_classes_to_correct_btn_cb():
            _set_default_classes_to_correct_setting()
            set_classes_list_settings_from_json(
                classes_list_widget=classes_to_correct_widget,
                settings=saved_classes_to_correct_settings,
            )
            _set_classes_to_correct_preview()
            g.updater("metas")

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="operation_type_text",
                    option_component=NodesFlow.WidgetOptionComponent(operation_type_text),
                ),
                NodesFlow.Node.Option(
                    name="operation_type_selector",
                    option_component=NodesFlow.WidgetOptionComponent(operation_type_selector),
                ),
                NodesFlow.Node.Option(
                    name="Select Class Mask",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=class_mask_edit_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(
                            class_mask_widgets_container
                        ),
                        sidebar_width=380,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="class_mask_preview",
                    option_component=NodesFlow.WidgetOptionComponent(class_mask_preview),
                ),
                NodesFlow.Node.Option(
                    name="Select Classes to correct",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=classes_to_correct_edit_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(
                            classes_to_correct_widgets_container
                        ),
                        sidebar_width=380,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="classes_to_correct_preview",
                    option_component=NodesFlow.WidgetOptionComponent(classes_to_correct_preview),
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
