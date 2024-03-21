import copy
from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import (
    NodesFlow,
    Button,
    Container,
    Flexbox,
    Text,
    Field,
    Select,
    Empty,
    ColorPicker,
    OneOf,
)
from supervisely import ProjectMeta
from supervisely.imaging.color import hex2rgb, rgb2hex

from src.ui.dtl import PixelLevelAction
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


class AnonymizeAction(PixelLevelAction):
    name = "anonymize"
    title = "Anonymize"
    docs_url = ""
    description = "Obscures image regions under objects of selected classes."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        _current_meta = ProjectMeta()
        classes_list_widget = ClassesList(multiple=True)
        classes_list_preview = ClassesListPreview(empty_text="No classes selected")
        classes_list_save_btn = create_save_btn()
        classes_list_set_default_btn = create_set_default_btn()
        classes_list_widget_field = Field(
            content=classes_list_widget,
            title="Classes",
            description="Select classes for which all objects will be removed",
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

        saved_classes_settings = []
        default_classes_settings = []

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

        def _set_default_classes_list_setting():
            # save setting to var
            nonlocal saved_classes_settings
            saved_classes_settings = copy.deepcopy(default_classes_settings)

        color_picker = ColorPicker()
        anon_items = [
            Select.Item("blur", "Blur", Empty()),
            Select.Item("color", "Pick Color", color_picker),
            Select.Item("class_color", "Same as Class Color", Empty()),
        ]
        anonymize_type_text = Text("Anonymization method", font_size=get_text_font_size())
        anonymize_type_select = Select(items=anon_items, size="small")
        anonymize_type_oneof = OneOf(anonymize_type_select)
        anonymize_type_container = Container(
            widgets=[
                anonymize_type_text,
                Flexbox(
                    widgets=[anonymize_type_select, anonymize_type_oneof],
                    gap=0,
                ),
            ],
            style="margin-top: 15px;",
            gap=4,
        )

        def data_changed_cb(**kwargs):
            project_meta = kwargs.get("project_meta", None)
            if project_meta is None:
                return
            nonlocal _current_meta
            if project_meta == _current_meta:
                return
            _current_meta = project_meta

            classes_list_widget.loading = True
            obj_classes = [cls for cls in project_meta.obj_classes]

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
            anon_type = anonymize_type_select.get_value()
            settings = {
                "classes": saved_classes_settings,
                "type": anon_type,
            }
            if anon_type == "color":
                settings["color"] = hex2rgb(color_picker.get_value())
            return settings

        def _set_settings_from_json(settings: dict):
            anon_type = settings.get("type", "blur")
            anonymize_type_select.set_value(anon_type)
            if anon_type == "color":
                color_picker.set_value(rgb2hex(settings["color"]))

            classes_list_widget.loading = True
            classes_list_settings = settings.get("classes", [])
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
            _set_default_classes_list_setting()
            set_classes_list_settings_from_json(
                classes_list_widget=classes_list_widget, settings=saved_classes_settings
            )
            _set_classes_list_preview()
            g.updater("metas")

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
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
                    "classes_preview",
                    option_component=NodesFlow.WidgetOptionComponent(classes_list_preview),
                ),
                NodesFlow.Node.Option(
                    "anonymize_type",
                    option_component=NodesFlow.WidgetOptionComponent(anonymize_type_container),
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
