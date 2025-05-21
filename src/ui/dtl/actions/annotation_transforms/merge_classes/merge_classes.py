from typing import Optional
import copy
from os.path import realpath, dirname

from supervisely import ProjectMeta
from supervisely.app.widgets import NodesFlow, Button, Container, Flexbox, Text, Field

from src.ui.dtl import AnnotationAction
from src.ui.dtl.Layer import Layer
from src.ui.widgets import ClassesMappingPreview, ClassesMappingSelector
from src.ui.dtl.utils import (
    get_classes_mapping_value,
    classes_mapping_settings_changed_meta,
    set_classes_mapping_preview,
    set_classes_mapping_settings_from_json,
    get_set_settings_button_style,
    get_set_settings_container,
    get_layer_docs,
    create_save_btn,
    create_set_default_btn,
    get_text_font_size,
)
import src.globals as g


class MergeClassesAction(AnnotationAction):
    name = "merge_classes"
    legacy_name = "merge_classes"
    docs_url = None
    title = "Merge Classes"
    description = "Merge existing classes into selected classes"
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        _current_meta = ProjectMeta()
        classes_mapping_widget = ClassesMappingSelector()
        classes_mapping_preview = ClassesMappingPreview()
        classes_mapping_save_btn = create_save_btn()
        classes_mapping_set_default_btn = create_set_default_btn()
        classes_mapping_widget_field = Field(
            content=classes_mapping_widget,
            title="Classes",
            description=(
                "Select source classes and target classes for merging. "
                "Source classes will be merged into target classes. "
                "Only classes with the same shape type can be merged, "
                "e.g. bitmap -> bitmap, polygon -> polygon, rectangle -> rectangle, etc."
            ),
        )
        classes_mapping_widgets_container = Container(
            widgets=[
                classes_mapping_widget_field,
                Flexbox(
                    widgets=[
                        classes_mapping_save_btn,
                        classes_mapping_set_default_btn,
                    ],
                    gap=110,
                ),
            ]
        )
        classes_mapping_edit_text = Text(
            "Merged classes: 0 / 0", status="text", font_size=get_text_font_size()
        )
        classes_mapping_edit_btn = Button(
            text="EDIT",
            icon="zmdi zmdi-edit",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )
        classes_mapping_edit_conatiner = get_set_settings_container(
            classes_mapping_edit_text, classes_mapping_edit_btn
        )

        saved_classes_mapping_settings = {}
        default_classes_mapping_settings = {}

        def _get_classes_mapping_value():
            return get_classes_mapping_value(
                classes_mapping_widget,
                default_action="skip",
                ignore_action="skip",
                other_allowed=False,
                default_allowed=False,
            )

        def _set_classes_mapping_preview():
            set_classes_mapping_preview(
                classes_mapping_widget,
                classes_mapping_preview,
                saved_classes_mapping_settings,
                default_action="skip",
                ignore_action="skip",
                classes_mapping_preview_text=classes_mapping_edit_text,
                classes_mapping_text_preview_title="Merged classes",
            )

        def _save_classes_mapping_setting():
            nonlocal saved_classes_mapping_settings
            saved_classes_mapping_settings = _get_classes_mapping_value()

        def _set_default_classes_mapping_setting():
            # save setting to var
            nonlocal saved_classes_mapping_settings
            saved_classes_mapping_settings = copy.deepcopy(default_classes_mapping_settings)

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            from src.compute.classes_utils import ClassConstants
            res_classes_mapping = {}
            for src_class, dst_class in saved_classes_mapping_settings.items():
                res_classes_mapping[src_class] = ClassConstants.MERGE + dst_class

            # add merge class to settings
            return {
                "classes_mapping": res_classes_mapping,
            }

        def data_changed_cb(**kwargs):
            project_meta = kwargs.get("project_meta", None)
            if project_meta is None:
                return
            nonlocal _current_meta
            if project_meta == _current_meta:
                return
            _current_meta = project_meta
            classes_mapping_widget.loading = True
            old_obj_classes = classes_mapping_widget.get_classes()

            # set classes to widget
            classes_mapping_widget.set(project_meta.obj_classes)

            # update settings according to new meta
            nonlocal saved_classes_mapping_settings
            saved_classes_mapping_settings = classes_mapping_settings_changed_meta(
                saved_classes_mapping_settings,
                old_obj_classes,
                project_meta.obj_classes,
                default_action="copy",
                ignore_action="skip",
                other_allowed=False,
            )

            # update classes mapping widget
            set_classes_mapping_settings_from_json(
                classes_mapping_widget,
                saved_classes_mapping_settings,
                missing_in_settings_action="ignore",
                missing_in_meta_action="ignore",
                select="unique",
            )

            # update settings preview
            _set_classes_mapping_preview()

            classes_mapping_widget.loading = False

        def _set_settings_from_json(settings):
            classes_mapping_settings = settings.get("classes_mapping", {})
            if classes_mapping_settings == "default":
                classes_mapping_widget.set_default()
            else:
                set_classes_mapping_settings_from_json(
                    classes_mapping_widget,
                    classes_mapping_settings,
                    missing_in_settings_action="ignore",
                    missing_in_meta_action="ignore",
                    select="unique",
                )

            # save settings
            _save_classes_mapping_setting()
            # update settings preview
            _set_classes_mapping_preview()

        @classes_mapping_save_btn.click
        def classes_mapping_save_btn_cb():
            _save_classes_mapping_setting()
            _set_classes_mapping_preview()
            g.updater("metas")

        @classes_mapping_set_default_btn.click
        def classes_mapping_set_default_btn_cb():
            _set_default_classes_mapping_setting()
            set_classes_mapping_settings_from_json(
                classes_mapping_widget,
                saved_classes_mapping_settings,
                missing_in_settings_action="ignore",
                missing_in_meta_action="ignore",
            )
            _set_classes_mapping_preview()
            g.updater("metas")

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="Set Classes Mapping",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=classes_mapping_edit_conatiner,
                        sidebar_component=NodesFlow.WidgetOptionComponent(
                            classes_mapping_widgets_container
                        ),
                        sidebar_width=380,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="classes_mapping_preview",
                    option_component=NodesFlow.WidgetOptionComponent(classes_mapping_preview),
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
