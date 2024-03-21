from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import (
    NodesFlow,
    Container,
    Select,
    InputNumber,
    OneOf,
    Field,
    Flexbox,
    Text,
    Slider,
)

from src.ui.dtl import PixelLevelAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs, get_slider_style, get_text_font_size


class BlurAction(PixelLevelAction):
    name = "blur"
    title = "Blur"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/transformation-layers/blur"
    description = "Applies blur filter to the image."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        _cur_kernel = 5
        kernel_input = InputNumber(value=_cur_kernel, min=3, max=255, step=2, size="small")

        sigma_slider = Slider(
            min=0.5,
            max=100,
            step=0.5,
            value=[0.5, 10],
            range=True,
            style=get_slider_style(),
        )
        sigma_preview_text = Text(
            text=f"min: {sigma_slider.get_value()[0]} - max: {sigma_slider.get_value()[1]}",
            status="text",
            font_size=get_text_font_size(),
        )

        blur_type_text = Text("Blur type", status="text", font_size=get_text_font_size())
        blur_selector = Select(
            items=[
                Select.Item(
                    "median",
                    "Median",
                    Field(
                        title="Kernel",
                        description="Set kernel to odd number",
                        content=kernel_input,
                    ),
                ),
                Select.Item(
                    "gaussian",
                    "Gaussian",
                    Field(
                        title="Sigma",
                        content=Container(
                            widgets=[
                                sigma_preview_text,
                                sigma_slider,
                            ]
                        ),
                    ),
                ),
            ],
            size="small",
        )
        blur_selector_oneof = OneOf(blur_selector)
        settings_preview = Container(
            widgets=[
                blur_type_text,
                blur_selector,
                blur_selector_oneof,
            ],
            gap=1,
        )

        saved_settings = {}

        def _update_preview():
            if blur_selector.get_value() == "gaussian":
                sigma_preview_text.set(
                    text=f"min: {sigma_slider.get_value()[0]} - max: {sigma_slider.get_value()[1]}",
                    status="text",
                )

        def _save_settings():
            nonlocal saved_settings
            settings = {
                "name": blur_selector.get_value(),
            }
            if settings["name"] == "median":
                settings["kernel"] = kernel_input.get_value()
            else:
                settings["sigma"] = {
                    "min": sigma_slider.get_value()[0],
                    "max": sigma_slider.get_value()[1],
                }
            saved_settings = settings
            _update_preview()

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return saved_settings

        def _set_settings_from_json(settings: dict):
            name = settings.get("name", "median")
            blur_selector.set_value(name)
            if name == "median":
                kernel_input.value = settings.get("kernel", 5)
            else:
                sigma_min_v = settings["sigma"].get("min", 3)
                sigma_max_v = settings["sigma"].get("max", 50)
                sigma_slider.set_value([sigma_min_v, sigma_max_v])
            _save_settings()

        @kernel_input.value_changed
        def kernel_input_cb(value):
            nonlocal _cur_kernel
            if value % 2 == 0:
                kernel_input.value = _cur_kernel
            else:
                _cur_kernel = value
            _save_settings()

        @sigma_slider.value_changed
        def sigma_slider_cb(value):
            _save_settings()

        @blur_selector.value_changed
        def blur_selector_cb(value):
            _save_settings()

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="Settings",
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
