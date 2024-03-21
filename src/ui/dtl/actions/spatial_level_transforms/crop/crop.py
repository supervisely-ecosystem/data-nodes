from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import (
    NodesFlow,
    Select,
    InputNumber,
    Container,
    OneOf,
    Field,
    Checkbox,
    Button,
    Text,
)

from src.ui.dtl import SpatialLevelAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import (
    get_set_settings_button_style,
    get_set_settings_container,
    get_layer_docs,
    create_save_btn,
    get_text_font_size,
)


class CropAction(SpatialLevelAction):
    name = "crop"
    title = "Crop"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/transformation-layers/crop"
    description = "Use to crop part of image with its annotations."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        crop_fixed_top = InputNumber(min=0)
        crop_fixed_left = InputNumber(min=0)
        crop_fixed_right = InputNumber(min=0)
        crop_fixed_bot = InputNumber(min=0)

        sides_crop_unit_selector = Select(
            items=[
                Select.Item("px", "pixels"),
                Select.Item("%", "percents"),
            ],
            size="small",
        )

        crop_fixed_container = Container(
            widgets=[
                Field(
                    content=sides_crop_unit_selector,
                    title="Crop unit",
                    description="Select measure unit for cropping: pixels or percents",
                ),
                Field(
                    title="top",
                    description="distance from the top of the image to the top of the crop",
                    content=crop_fixed_top,
                ),
                Field(
                    title="left",
                    description="distance from the left of the image to the left of the crop",
                    content=crop_fixed_left,
                ),
                Field(
                    title="right",
                    description="distance from the right of the image to the right of the crop",
                    content=crop_fixed_right,
                ),
                Field(
                    title="bottom",
                    description="distance from the bottom of the image to the bottom of the crop",
                    content=crop_fixed_bot,
                ),
            ]
        )
        crop_random_height_min = InputNumber(min=0, max=100)
        crop_random_height_max = InputNumber(min=0, max=100)
        crop_random_height = Container(
            widgets=[
                Field(
                    title="min %",
                    description="minimum height of resulting crop (in percent wrt to image height)",
                    content=crop_random_height_min,
                ),
                Field(
                    title="max %",
                    description="maximum height of resulting crop (in percent wrt to image height)",
                    content=crop_random_height_max,
                ),
            ]
        )
        crop_random_width_min = InputNumber(min=0, max=100)
        crop_random_width_max = InputNumber(min=0, max=100)
        crop_random_width = Container(
            widgets=[
                Field(
                    title="min %",
                    description="minimum width of resulting crop (in percent wrt to image width)",
                    content=crop_random_width_min,
                ),
                Field(
                    title="max %",
                    description="maximum width of resulting crop (in percent wrt to image width)",
                    content=crop_random_width_max,
                ),
            ]
        )
        crop_random_keep_aspect_ratio = Checkbox(content="Keep aspect ratio")
        crop_random_container = Container(
            widgets=[
                Field(title="Height", content=crop_random_height),
                Field(title="Width", content=crop_random_width),
                Field(
                    title="Keep aspect ratio",
                    description="should resulting random crop have the same aspect ratio as a source image",
                    content=crop_random_keep_aspect_ratio,
                ),
            ]
        )

        mode_select = Select(
            items=[
                Select.Item("sides", "Sides", crop_fixed_container),
                Select.Item("random_part", "Random part", crop_random_container),
            ],
            size="small",
        )
        mode_select_field = Field(
            content=mode_select,
            title="Mode",
            description="Select mode of cropping: by sides or random part of image",
        )

        mode_preview = Text("", status="text", font_size=get_text_font_size())
        params_preview = Text("", status="text", font_size=get_text_font_size())
        settings_preview = Container(widgets=[mode_preview, params_preview], gap=1)

        save_settings_btn = create_save_btn()
        settings_container = Container(
            widgets=[mode_select_field, OneOf(mode_select), save_settings_btn]
        )
        settings_edit_text = Text("Settings", status="text", font_size=get_text_font_size())
        settings_edit_btn = Button(
            text="EDIT",
            icon="zmdi zmdi-edit",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )
        settings_edit_container = get_set_settings_container(settings_edit_text, settings_edit_btn)

        saved_settings = {}

        def _validate_percent_value(value, input_num_widget):
            if sides_crop_unit_selector.get_value() == "%":
                if value > 100:
                    input_num_widget.value = 100

        @crop_fixed_top.value_changed
        def update_crop_fixed_top(value):
            _validate_percent_value(value, crop_fixed_top)

        @crop_fixed_left.value_changed
        def update_crop_fixed_left(value):
            _validate_percent_value(value, crop_fixed_left)

        @crop_fixed_right.value_changed
        def update_crop_fixed_right(value):
            _validate_percent_value(value, crop_fixed_right)

        @crop_fixed_bot.value_changed
        def update_crop_fixed_bot(value):
            _validate_percent_value(value, crop_fixed_bot)

        @crop_random_width_min.value_changed
        def update_crop_random_width_min(value):
            if crop_random_width_max.value < value:
                crop_random_width_max.value = value

        @crop_random_width_max.value_changed
        def update_crop_random_width_max(value):
            if value < crop_random_width_min.value:
                crop_random_width_min.value = value

        @crop_random_height_min.value_changed
        def update_crop_random_height_min(value):
            if crop_random_height_max.value < value:
                crop_random_height_max.value = value

        @crop_random_height_max.value_changed
        def update_crop_random_height_max(value):
            if value < crop_random_height_min.value:
                crop_random_height_min.value = value

        @sides_crop_unit_selector.value_changed
        def update_crop_fixed_unit(value):
            if value == "%":
                if crop_fixed_top.value > 100:
                    crop_fixed_top.value = 100
                if crop_fixed_left.value > 100:
                    crop_fixed_left.value = 100
                if crop_fixed_right.value > 100:
                    crop_fixed_right.value = 100
                if crop_fixed_bot.value > 100:
                    crop_fixed_bot.value = 100

        def _get_sides():
            crop_unit = sides_crop_unit_selector.get_value()
            return {
                "top": str(crop_fixed_top.get_value()) + crop_unit,
                "left": str(crop_fixed_left.get_value()) + crop_unit,
                "right": str(crop_fixed_right.get_value()) + crop_unit,
                "bottom": str(crop_fixed_bot.get_value()) + crop_unit,
            }

        def _get_random():
            return {
                "height": {
                    "min_percent": crop_random_height_min.get_value(),
                    "max_percent": crop_random_height_max.get_value(),
                },
                "width": {
                    "min_percent": crop_random_width_min.get_value(),
                    "max_percent": crop_random_width_max.get_value(),
                },
                "keep_aspect_ratio": crop_random_keep_aspect_ratio.is_checked(),
            }

        def _update_preview():
            mode = "sides" if "sides" in saved_settings else "random_part"
            if mode == "":
                mode_preview.text = ""
                params_preview.text = ""
            elif mode == "sides":
                sides = _get_sides()
                mode_preview.text = "Mode: Sides"
                params_preview.text = f"Top: {sides['top']}<br>Left: {sides['left']}<br>Right: {sides['right']}<br>Bottom: {sides['bottom']}"
            elif mode == "random_part":
                random_part = _get_random()
                mode_preview.text = "Mode: Random part"
                params_preview.text = f"Height: min {random_part['height']['min_percent']}% - max {random_part['height']['max_percent']}%<br>Width: min {random_part['width']['min_percent']}% - max {random_part['width']['max_percent']}%<br>Keep aspect ratio: {random_part['keep_aspect_ratio']}"

        def _save_settings():
            nonlocal saved_settings
            settings = {}
            mode = mode_select.get_value()
            if mode == "sides":
                settings["sides"] = _get_sides()
            else:
                settings["random_part"] = _get_random()
            saved_settings = settings
            _update_preview()

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return saved_settings

        def _set_sides(settings: dict):
            mode_select.set_value("sides")
            top_value = settings["sides"]["top"]
            left_value = settings["sides"]["left"]
            right_value = settings["sides"]["right"]
            bot_value = settings["sides"]["bottom"]

            if top_value.endswith("%"):
                sides_crop_unit_selector.set_value("%")
                crop_unit_slice = -1
            else:
                sides_crop_unit_selector.set_value("px")
                crop_unit_slice = -2

            crop_fixed_top.value = int(top_value[:crop_unit_slice])
            crop_fixed_left.value = int(left_value[:crop_unit_slice])
            crop_fixed_right.value = int(right_value[:crop_unit_slice])
            crop_fixed_bot.value = int(bot_value[:crop_unit_slice])
            mode_select.set_value("sides")

        def _set_random(settings: dict):
            h_min = settings["random_part"]["height"]["min_percent"]
            h_max = settings["random_part"]["height"]["max_percent"]
            w_min = settings["random_part"]["width"]["min_percent"]
            w_max = settings["random_part"]["width"]["max_percent"]

            crop_random_height_min.value = h_min
            crop_random_height_max.value = h_max
            crop_random_width_min.value = w_min
            crop_random_width_max.value = w_max
            if settings["random_part"]["keep_aspect_ratio"]:
                crop_random_keep_aspect_ratio.check()
            else:
                crop_random_keep_aspect_ratio.uncheck()
            mode_select.set_value("random_part")

        def _set_settings_from_json(settings):
            if "sides" in settings:
                _set_sides(settings)
            elif "random_part" in settings:
                _set_random(settings)
            _save_settings()

        save_settings_btn.click(_save_settings)

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="Set Settings",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=settings_edit_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(settings_container),
                        sidebar_width=300,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="settings_preview",
                    option_component=NodesFlow.WidgetOptionComponent(settings_preview),
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
        )
