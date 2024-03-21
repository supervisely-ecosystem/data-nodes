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
    Switch,
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


class FilterVideosByObject(FilterAndConditionAction):
    name = "filter_videos_by_object"
    title = "Filter Videos by Objects"
    docs_url = None
    description = "Filter Videos based on the presence of objects of specified classes."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        saved_include_classes = "default"
        saved_exclude_classes = []
        default_include_classes = "default"
        default_exclude_classes = []
        _current_meta = ProjectMeta()

        include_classes_list_widget = ClassesList(multiple=True)
        include_switch = Switch(switched=True)
        include_classes_list_field = Field(
            title="Video have objects of classes below",
            description="Please, select classes that have to be presented on the video",
            content=include_switch,
        )

        @include_switch.value_changed
        def include_switched(is_switched):
            if is_switched:
                include_classes_list_widget.show()
            else:
                include_classes_list_widget.hide()

        exclude_classes_list_widget = ClassesList(multiple=True)
        exclude_classes_list_widget.hide()
        exclude_switch = Switch(switched=False)

        @exclude_switch.value_changed
        def exclude_swithced(is_switched):
            if is_switched:
                exclude_classes_list_widget.show()
            else:
                exclude_classes_list_widget.hide()

        exclude_classes_list_field = Field(
            title="Video have no objects of classes below",
            description="Please, select classes that should not be presented on the video",
            content=exclude_switch,
        )

        @include_classes_list_widget.selection_changed
        def include_classes_list_selection_changed(selected):
            exclude_classes_list_widget.deselect([cls.name for cls in selected])

        @exclude_classes_list_widget.selection_changed
        def exclude_classes_list_selection_changed(selected):
            include_classes_list_widget.deselect([cls.name for cls in selected])

        description = Container(
            widgets=[Text("Video will be passed to the True branch if:")],
            style="margin-top: 25px;",
        )
        settings_save_btn = create_save_btn()
        settings_set_default_btn = create_set_default_btn()
        settings_widgets_container = Container(
            widgets=[
                description,
                include_classes_list_field,
                include_classes_list_widget,
                Text("<b>AND</b>"),
                exclude_classes_list_field,
                exclude_classes_list_widget,
                Flexbox(
                    widgets=[
                        settings_save_btn,
                        settings_set_default_btn,
                    ],
                    gap=110,
                ),
            ]
        )
        settings_edit_text = Text("Condition", status="text", font_size=get_text_font_size())
        settings_edit_btn = Button(
            text="EDIT",
            icon="zmdi zmdi-edit",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )
        settings_edit_container = get_set_settings_container(settings_edit_text, settings_edit_btn)

        include_preview = ClassesListPreview()
        exclude_preview = ClassesListPreview()
        with_container = Container(
            widgets=[
                Text("Video has objects:"),
                include_preview,
            ]
        )
        without_container = Container(
            widgets=[
                Text("Video doesn't have objects:"),
                exclude_preview,
            ]
        )
        and_text = Text('<span style="display: block; padding: 10px 0px 5px 2px;">AND</span>')
        no_condition_text = NotificationBox(
            title="No condition", description="Select filtering classes"
        )
        settings_preview = Container(
            widgets=[with_container, and_text, without_container, no_condition_text], gap=0
        )

        def _get_include_classes_value():
            return get_classes_list_value(include_classes_list_widget, multiple=True)

        def _get_exclude_classes_value():
            return get_classes_list_value(exclude_classes_list_widget, multiple=True)

        def _save_include_classes_setting():
            nonlocal saved_include_classes
            if include_switch.is_switched():
                saved_include_classes = _get_include_classes_value()
            else:
                saved_include_classes = []

        def _save_exclude_classes_setting():
            nonlocal saved_exclude_classes
            if exclude_switch.is_switched():
                saved_exclude_classes = _get_exclude_classes_value()
            else:
                saved_exclude_classes = []

        def _set_include_preview():
            set_classes_list_preview(
                include_classes_list_widget,
                include_preview,
                saved_include_classes,
            )

        def _set_exclude_preview():
            set_classes_list_preview(
                exclude_classes_list_widget,
                exclude_preview,
                saved_exclude_classes,
            )

        def _set_previews():
            _set_include_preview()
            _set_exclude_preview()
            include_classes = include_preview.get()
            exclude_classes = exclude_preview.get()
            if include_classes:
                with_container.show()
            else:
                with_container.hide()
            if exclude_classes:
                without_container.show()
            else:
                without_container.hide()
            if include_classes and exclude_classes:
                and_text.show()
            else:
                and_text.hide()
            if include_classes or exclude_classes:
                no_condition_text.hide()
            else:
                no_condition_text.show()

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            nonlocal saved_include_classes, saved_exclude_classes
            include = saved_include_classes
            if saved_include_classes == "default":
                include = _get_include_classes_value()
            exclude = saved_exclude_classes
            if saved_exclude_classes == "default":
                exclude = _get_exclude_classes_value()
            return {
                "include": include,
                "exclude": exclude,
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
            include_classes_list_widget.set(obj_classes)
            exclude_classes_list_widget.set(obj_classes)

            # update settings according to new meta
            nonlocal saved_include_classes, saved_exclude_classes
            saved_include_classes = classes_list_settings_changed_meta(
                saved_include_classes, obj_classes
            )
            saved_exclude_classes = classes_list_settings_changed_meta(
                saved_exclude_classes, obj_classes
            )

            # update classes list widgets
            set_classes_list_settings_from_json(
                include_classes_list_widget,
                saved_include_classes,
            )
            set_classes_list_settings_from_json(
                exclude_classes_list_widget,
                saved_exclude_classes,
            )

            # update settings preview
            _set_previews()
            settings_widgets_container.loading = False

        @settings_save_btn.click
        def save_settings_handler():
            _save_include_classes_setting()
            _save_exclude_classes_setting()
            _set_previews()
            g.updater("metas")

        @settings_set_default_btn.click
        def set_default_settings_handler():
            nonlocal saved_include_classes, saved_exclude_classes
            saved_include_classes = copy.deepcopy(default_include_classes)
            saved_exclude_classes = copy.deepcopy(default_exclude_classes)
            _set_previews()
            g.updater("metas")

        def _set_settings_from_json(settings):
            include = settings.get("include", default_include_classes)
            exclude = settings.get("exclude", default_exclude_classes)
            set_classes_list_settings_from_json(include_classes_list_widget, include)
            if include:
                include_classes_list_widget.show()
                include_switch.on()
            else:
                include_classes_list_widget.hide()
                include_switch.off()
            set_classes_list_settings_from_json(exclude_classes_list_widget, exclude)
            if exclude:
                exclude_classes_list_widget.show()
                exclude_switch.on()
            else:
                exclude_classes_list_widget.hide()
                exclude_switch.off()

            # save settings
            if include != "default":
                _save_include_classes_setting()
            if exclude != "default":
                _save_exclude_classes_setting()

            # update settings preview
            _set_include_preview()
            _set_exclude_preview()

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="Set Condition",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=settings_edit_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(
                            settings_widgets_container
                        ),
                        sidebar_width=380,
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
