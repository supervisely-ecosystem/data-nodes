import copy
from os.path import realpath, dirname
from typing import Optional

from supervisely.app.widgets import NodesFlow, Button, Container, Flexbox, Text, Field
from supervisely import ProjectMeta, Rectangle, AnyGeometry

from src.ui.dtl import AnnotationAction
from src.ui.dtl.Layer import Layer
from src.ui.widgets import ClassesList, ClassesListPreview
from src.ui.dtl.utils import (
    classes_list_to_mapping,
    classes_mapping_settings_changed_meta,
    get_set_settings_button_style,
    get_set_settings_container,
    get_layer_docs,
    create_save_btn,
    create_set_default_btn,
    get_classes_list_value,
    mapping_to_list,
    set_classes_list_preview,
    set_classes_list_settings_from_json,
    get_text_font_size,
)
import src.globals as g


class BboxToPolygonAction(AnnotationAction):
    name = "bbox_to_polygon"
    legacy_name = "bbox2poly"
    title = "BBox to Polygon"
    docs_url = (
        "https://docs.supervisely.com/data-manipulation/index/transformation-layers/bbox2poly"
    )
    description = 'Converts rectangles ("bounding boxes") to polygons.'
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        _current_meta = ProjectMeta()
        classes_mapping_widget = ClassesList(multiple=True)
        classes_mapping_widget_field = Field(
            content=classes_mapping_widget,
            title="Classes",
            description="Select classes to convert them to POLYGON",
        )
        classes_mapping_preview = ClassesListPreview()
        classes_mapping_save_btn = create_save_btn()
        classes_mapping_set_default_btn = create_set_default_btn()
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
        classes_mapping_edit_text = Text("Classes", status="text", font_size=get_text_font_size())
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

        saved_classes_mapping_settings = "default"
        default_classes_mapping_settings = "default"

        def _get_classes_mapping_value():
            classes = get_classes_list_value(classes_mapping_widget, multiple=True)
            return classes_list_to_mapping(
                classes, [oc.name for oc in _current_meta.obj_classes], other="skip"
            )

        def _set_classes_mapping_preview():
            set_classes_list_preview(
                classes_mapping_widget,
                classes_mapping_preview,
                (
                    "default"
                    if saved_classes_mapping_settings == "default"
                    else mapping_to_list(saved_classes_mapping_settings)
                ),
                classes_mapping_edit_text,
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
            classes_mapping = saved_classes_mapping_settings
            if saved_classes_mapping_settings == "default":
                classes_mapping = _get_classes_mapping_value()
            return {
                "classes_mapping": classes_mapping,
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
            old_obj_classes = project_meta.obj_classes
            new_obj_classes = [
                obj_class
                for obj_class in project_meta.obj_classes
                if obj_class.geometry_type in [Rectangle, AnyGeometry]
            ]

            # set classes to widget
            classes_mapping_widget.set(new_obj_classes)

            # update settings according to new meta
            nonlocal saved_classes_mapping_settings
            saved_classes_mapping_settings = classes_mapping_settings_changed_meta(
                saved_classes_mapping_settings,
                old_obj_classes,
                new_obj_classes,
                default_action="copy",
                ignore_action="skip",
                other_allowed=False,
            )

            # update classes mapping widget
            set_classes_list_settings_from_json(
                classes_mapping_widget, saved_classes_mapping_settings
            )

            # update settings preview
            _set_classes_mapping_preview()

            classes_mapping_widget.loading = False

        def _set_settings_from_json(settings):
            classes_list_settings = settings.get(
                "classes_mapping", default_classes_mapping_settings
            )
            set_classes_list_settings_from_json(
                classes_list_widget=classes_mapping_widget, settings=classes_list_settings
            )

            if classes_list_settings != "default":
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
            set_classes_list_settings_from_json(
                classes_mapping_widget,
                saved_classes_mapping_settings,
            )
            _set_classes_mapping_preview()
            g.updater("metas")

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="Set Classes",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=classes_mapping_edit_conatiner,
                        sidebar_component=NodesFlow.WidgetOptionComponent(
                            classes_mapping_widgets_container
                        ),
                        sidebar_width=380,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="Classes Mapping Preview",
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
            need_preview=True if g.MODALITY_TYPE == "images" else False,
        )
