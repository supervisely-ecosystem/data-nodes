import copy
from typing import Optional
from os.path import realpath, dirname

from supervisely import ProjectMeta
from supervisely.app.widgets import (
    NodesFlow,
    Flexbox,
    Container,
    Field,
    Text,
    Button,
    NotificationBox,
)

from src.ui.dtl.Action import FilterAndConditionAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import (
    create_save_btn,
    create_set_default_btn,
    get_classes_list_value,
    get_layer_docs,
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
    set_classes_list_preview,
    set_classes_list_settings_from_json,
    classes_list_settings_changed_meta,
)
from src.ui.widgets import ClassesList, ClassesListPreview
import src.globals as g


class FilterImageWithoutObjects(FilterAndConditionAction):
    name = "filter_image_without_objects"
    title = "Filter Images without Objects"
    docs_url = ""
    description = "Filter Images based on the presence of objects."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        saved_exclude_classes = "default"
        default_exclude_classes = "default"
        _current_meta = ProjectMeta()

        exclude_classes_list_widget = ClassesList(multiple=True)
        exclude_classes_list_field = Field(
            title="Select which classes should not be presented on the image",
            description=(
                "Images without objects of the selected classes will be filtered out to the output branch 'True', "
                "rest of the images will be filtered out to the output branch 'False'."
            ),
            content=exclude_classes_list_widget,
        )

        settings_save_btn = create_save_btn()
        settings_set_default_btn = create_set_default_btn()
        settings_widgets_container = Container(
            widgets=[
                exclude_classes_list_field,
                Flexbox(
                    widgets=[
                        settings_save_btn,
                        settings_set_default_btn,
                    ],
                    gap=110,
                ),
            ]
        )
        settings_edit_text = Text(
            "Image doesn't have objects:", status="text", font_size=get_text_font_size()
        )
        settings_edit_btn = Button(
            text="EDIT",
            icon="zmdi zmdi-edit",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )
        settings_edit_container = get_set_settings_container(settings_edit_text, settings_edit_btn)

        exclude_preview = ClassesListPreview()
        without_container = exclude_preview
        no_condition_text = NotificationBox(
            title="No classes", description="Select filtering classes"
        )
        settings_preview = Container(widgets=[without_container, no_condition_text], gap=0)

        def _get_exclude_classes_value():
            return get_classes_list_value(exclude_classes_list_widget, multiple=True)

        def _save_exclude_classes_setting():
            nonlocal saved_exclude_classes
            saved_exclude_classes = _get_exclude_classes_value()

        def _set_exclude_preview():
            set_classes_list_preview(
                exclude_classes_list_widget,
                exclude_preview,
                saved_exclude_classes,
            )

        def _set_previews():
            _set_exclude_preview()
            exclude_classes = exclude_preview.get()
            if exclude_classes:
                no_condition_text.hide()

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            nonlocal saved_exclude_classes
            exclude_classes = saved_exclude_classes
            if saved_exclude_classes == "default":
                exclude_classes = _get_exclude_classes_value()
            return {
                "exclude_classes": exclude_classes,
            }

        def data_changed_cb(**kwargs):
            project_meta = kwargs.get("project_meta", None)
            if project_meta is None:
                return
            nonlocal _current_meta
            if project_meta == _current_meta:
                return
            _current_meta = project_meta
            settings_widgets_container.loading = True
            obj_classes = project_meta.obj_classes  # Why change?

            # set classes to widgets
            exclude_classes_list_widget.set(obj_classes)

            # update settings according to new meta
            nonlocal saved_exclude_classes
            saved_exclude_classes = classes_list_settings_changed_meta(
                saved_exclude_classes, obj_classes
            )

            # update classes list widgets
            set_classes_list_settings_from_json(
                exclude_classes_list_widget,
                saved_exclude_classes,
            )

            # update settings preview
            _set_previews()
            settings_widgets_container.loading = False

        @settings_save_btn.click
        def save_settings_handler():
            _save_exclude_classes_setting()
            _set_previews()
            g.updater("metas")

        @settings_set_default_btn.click
        def set_default_settings_handler():
            nonlocal saved_exclude_classes
            saved_exclude_classes = copy.deepcopy(default_exclude_classes)
            _set_previews()
            g.updater("metas")

        def _set_settings_from_json(settings):
            exclude_classes = settings.get("exclude_classes", default_exclude_classes)
            set_classes_list_settings_from_json(exclude_classes_list_widget, exclude_classes)

            # save settings
            if exclude_classes != "default":
                _save_exclude_classes_setting()

            # update settings preview
            _set_exclude_preview()

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="Set exclude classes",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=settings_edit_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(
                            settings_widgets_container
                        ),
                        sidebar_width=400,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="Settings Preview",
                    option_component=NodesFlow.WidgetOptionComponent(settings_preview),
                ),
            ]
            return {
                "src": [],
                "dst": [],
                "settings": settings_options,
            }

        _set_previews()
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
