from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import NodesFlow, Button, Container, Text, Field
from supervisely import ProjectMeta
from supervisely.imaging.color import hex2rgb, rgb2hex

from src.ui.dtl import AnnotationAction
from src.ui.dtl.Layer import Layer
from src.ui.widgets import ClassesColorMapping, ClassesMappingPreview
from src.ui.dtl.utils import (
    get_set_settings_button_style,
    get_set_settings_container,
    get_layer_docs,
    create_save_btn,
    get_text_font_size,
)


class ChangeClassColorAction(AnnotationAction):
    name = "change_class_color"
    legacy_name = "color_class"
    title = "Change Class Color"
    description = "Use for changing colors of the classes. Add this layer at the end of graph, before data saving."
    docs_url = (
        "https://docs.supervisely.com/data-manipulation/index/transformation-layers/color_class"
    )
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        _current_meta = ProjectMeta()
        classes_colors = ClassesColorMapping()
        classes_colors_preview = ClassesMappingPreview()
        classes_colors_save_btn = create_save_btn()
        classes_colors_widgets_container = Container(
            widgets=[classes_colors, classes_colors_save_btn]
        )
        classes_colors_widget_field = Field(
            content=classes_colors_widgets_container,
            title="Classes",
            description="Select the classes for which you want to change the color",
        )
        classes_colors_edit_text = Text(
            "Classes Colors: 0 / 0", status="text", font_size=get_text_font_size()
        )
        classes_colors_edit_btn = Button(
            text="EDIT",
            icon="zmdi zmdi-edit",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )
        classes_colors_edit_conatiner = get_set_settings_container(
            classes_colors_edit_text, classes_colors_edit_btn
        )

        saved_classes_colors_settings = {}

        def _save_classes_colors_setting():
            nonlocal saved_classes_colors_settings
            mapping = classes_colors.get_mapping()
            saved_classes_colors_settings = {
                cls_name: hex2rgb(value["value"])
                for cls_name, value in mapping.items()
                if value["selected"]
            }
            obj_classes = classes_colors.get_selected_classes()
            classes_colors_preview.set(
                obj_classes, {k: rgb2hex(v) for k, v in saved_classes_colors_settings.items()}
            )
            classes_colors_edit_text.set(
                f"Classes Colors: {len(obj_classes)} / {len(_current_meta.obj_classes)}", "text"
            )

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return {"classes_color_mapping": saved_classes_colors_settings}

        def data_changed_cb(**kwargs):
            project_meta = kwargs.get("project_meta", None)
            if project_meta is None:
                return
            nonlocal _current_meta
            if project_meta == _current_meta:
                return
            _current_meta = project_meta
            classes_colors.loading = True
            classes_colors.set(project_meta.obj_classes)
            _set_settings_from_json(get_settings({}))
            _save_classes_colors_setting()
            classes_colors.loading = False

        def _set_settings_from_json(settings: dict):
            colors = settings.get("classes_color_mapping", {})
            classes_colors.loading = True
            classes_colors.set_colors(
                [
                    colors.get(cls, hex2rgb(value["value"]))
                    for cls, value in classes_colors.get_mapping().items()
                ]
            )
            classes_colors.select([cls_name for cls_name in colors.keys()])
            _save_classes_colors_setting()
            classes_colors.loading = False

        classes_colors_save_btn.click(_save_classes_colors_setting)

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)

            settings_options = [
                NodesFlow.Node.Option(
                    name="Set Colors",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=classes_colors_edit_conatiner,
                        sidebar_component=NodesFlow.WidgetOptionComponent(
                            classes_colors_widget_field
                        ),
                        sidebar_width=450,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="colors_preview",
                    option_component=NodesFlow.WidgetOptionComponent(classes_colors_preview),
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
