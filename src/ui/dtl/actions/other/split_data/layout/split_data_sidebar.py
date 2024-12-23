from supervisely.app.widgets import (
    Container,
    Button,
    Field,
    Select,
    Slider,
    InputNumber,
)
from src.ui.dtl.utils import create_save_btn


def create_sidebar_widgets():
    # Sidebar Initialization widgets

    sidebar_percent_slider = Slider(
        show_input=True, show_input_controls=True, min=1, max=100, step=1, value=50
    )
    sidebar_percent_field = Field(
        sidebar_percent_slider,
        "Select percentage",
        "Select percentage by which to distribute images across datasets",
    )

    sidebar_number_input = InputNumber(min=1, max=None, value=50)
    sidebar_number_field = Field(
        sidebar_number_input,
        "Select number of images",
        "Select number of images to include in datasets",
    )
    sidebar_number_field.hide()

    sidebar_parts_input = InputNumber(min=1, max=None, value=5)
    sidebar_parts_field = Field(
        sidebar_parts_input,
        "Select number of parts",
        "Select number of datasets to split data into. Resulting datasets will have equal number of images",
    )
    sidebar_parts_field.hide()

    sidebar_items = [
        Select.Item("percent", "by percent"),
        Select.Item("number", "by number"),
        Select.Item("classes", "by classes"),
        Select.Item("tags", "by tags"),
        Select.Item("parts", "by parts"),
    ]
    sidebar_selector = Select(sidebar_items)

    sidebar_save_button = create_save_btn()
    sidebar_container = Container(
        [
            sidebar_selector,
            sidebar_percent_field,
            sidebar_number_field,
            sidebar_parts_field,
            sidebar_save_button,
        ]
    )
    sidebar_selector_field = Field(
        sidebar_container,
        "How to split data",
        "Select on which basis want your data to be distributed across datasets",
    )

    return (
        sidebar_selector,
        sidebar_selector_field,
        sidebar_percent_slider,
        sidebar_percent_field,
        sidebar_number_input,
        sidebar_number_field,
        sidebar_parts_input,
        sidebar_parts_field,
        sidebar_save_button,
    )
