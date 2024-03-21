import copy
from typing import Optional
from os.path import realpath, dirname

from supervisely import ProjectMeta
from supervisely.app.widgets import (
    NodesFlow,
    InputNumber,
    Container,
    Field,
    Flexbox,
    Button,
    Text,
    Select,
    Field,
)

from src.ui.dtl import SpatialLevelAction
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


class InstancesCropAction(SpatialLevelAction):
    name = "instances_crop"
    title = "Instances Crop"
    docs_url = (
        "https://docs.supervisely.com/data-manipulation/index/transformation-layers/instances_crop"
    )
    description = "Crops objects of specified classes from image with configurable padding."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        _current_meta = ProjectMeta()
        classes_list_widget = ClassesList(multiple=True)
        classes_list_preview = ClassesListPreview()
        classes_list_save_btn = create_save_btn()
        classes_list_set_default_btn = create_set_default_btn()
        classes_list_widget_field = Field(
            content=classes_list_widget,
            title="Classes",
            description="Select classes to get cropped images for their objects",
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

        padding_top = InputNumber(min=0)
        padding_left = InputNumber(min=0)
        padding_right = InputNumber(min=0)
        padding_bot = InputNumber(min=0)

        padding_preview = Text("", status="text", font_size=get_text_font_size())
        save_padding_btn = create_save_btn()

        padding_unit_selector = Select(
            items=[
                Select.Item("px", "pixels"),
                Select.Item("%", "percents"),
            ],
            size="small",
        )

        padding_container = Container(
            widgets=[
                Field(
                    content=padding_unit_selector,
                    title="Crop unit",
                    description="Select measure unit for cropping: pixels or percents",
                ),
                Field(title="Top padding", content=padding_top),
                Field(title="Left padding", content=padding_left),
                Field(title="Right padding", content=padding_right),
                Field(title="Bottom padding", content=padding_bot),
                save_padding_btn,
            ]
        )
        padding_edit_text = Text("Padding", status="text", font_size=get_text_font_size())
        padding_edit_btn = Button(
            text="EDIT",
            icon="zmdi zmdi-edit",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )
        padding_edit_container = get_set_settings_container(padding_edit_text, padding_edit_btn)

        def _validate_percent_value(value, input_num_widget):
            if padding_unit_selector.get_value() == "%":
                if value > 100:
                    input_num_widget.value = 100

        @padding_top.value_changed
        def update_padding_top(value):
            _validate_percent_value(value, padding_top)

        @padding_left.value_changed
        def update_padding_left(value):
            _validate_percent_value(value, padding_left)

        @padding_right.value_changed
        def update_padding_right(value):
            _validate_percent_value(value, padding_right)

        @padding_bot.value_changed
        def update_padding_bot(value):
            _validate_percent_value(value, padding_bot)

        @padding_unit_selector.value_changed
        def update_crop_fixed_unit(value):
            if value == "%":
                if padding_top.value > 100:
                    padding_top.value = 100
                if padding_left.value > 100:
                    padding_left.value = 100
                if padding_right.value > 100:
                    padding_right.value = 100
                if padding_bot.value > 100:
                    padding_bot.value = 100

        def _get_padding():
            return {
                "sides": {
                    "top": f"{padding_top.get_value()}{padding_unit_selector.get_value()}",
                    "left": f"{padding_left.get_value()}{padding_unit_selector.get_value()}",
                    "right": f"{padding_right.get_value()}{padding_unit_selector.get_value()}",
                    "bottom": f"{padding_bot.get_value()}{padding_unit_selector.get_value()}",
                }
            }

        saved_padding_settings = {}

        def _save_padding():
            nonlocal saved_padding_settings
            saved_padding_settings = _get_padding()
            padding_preview.text = f'Top: {saved_padding_settings["sides"]["top"]}<br>Left: {saved_padding_settings["sides"]["left"]}<br>Right: {saved_padding_settings["sides"]["right"]}<br>Bottom: {saved_padding_settings["sides"]["bottom"]}'

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            classes = saved_classes_settings
            if saved_classes_settings == "default":
                classes = _get_classes_list_value()
            return {
                "classes": classes,
                "pad": saved_padding_settings,
            }

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

            classes_names = saved_classes_settings
            if classes_names == "default":
                classes_names = [cls.name for cls in obj_classes]
            classes_list_widget.select(classes_names)

            # update settings preview
            _set_classes_list_preview()

            classes_list_widget.loading = False

        save_padding_btn.click(_save_padding)

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

        def _set_padding(settings: dict):
            if "pad" in settings:
                top_value = settings["pad"]["sides"]["top"]
                left_value = settings["pad"]["sides"]["left"]
                right_value = settings["pad"]["sides"]["right"]
                bot_value = settings["pad"]["sides"]["bottom"]

                if top_value.endswith("%"):
                    padding_unit_selector.set_value("%")
                    crop_unit_slice = -1
                else:
                    padding_unit_selector.set_value("px")
                    crop_unit_slice = -2

                padding_top.value = int(top_value[:crop_unit_slice])
                padding_left.value = int(left_value[:crop_unit_slice])
                padding_right.value = int(right_value[:crop_unit_slice])
                padding_bot.value = int(bot_value[:crop_unit_slice])

        def _set_settings_from_json(settings: dict):
            padding_container.loading = True
            _set_padding(settings)
            _save_padding()
            padding_container.loading = False
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
                    name="classes_preview",
                    option_component=NodesFlow.WidgetOptionComponent(classes_list_preview),
                ),
                NodesFlow.Node.Option(
                    name="Set Padding",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=padding_edit_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(padding_container),
                        sidebar_width=380,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="padding_preview",
                    option_component=NodesFlow.WidgetOptionComponent(padding_preview),
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
