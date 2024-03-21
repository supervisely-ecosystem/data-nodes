from src.ui.dtl.utils import (
    create_save_btn,
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
)
from supervisely.app.widgets import Button, Container, Text, Input, TextArea, Field


def create_job_description_widgets():
    # SIDEBAR SETTINGS
    lj_description_title_input = Input(value="Labeling Job", placeholder="Labeling Job")
    lj_description_title_field = Field(
        title="Title",
        description="Name of the labeling job",
        content=lj_description_title_input,
    )

    lj_description_description_editor = TextArea(placeholder="Enter short description", rows=5)
    lj_description_description_field = Field(
        title="Short Description",
        description="Short description of the labeling job",
        content=lj_description_description_editor,
    )

    lj_description_readme_editor = TextArea(
        placeholder="Add detailed description for labeling job", rows=10
    )
    lj_description_readme_field = Field(
        title="Readme",
        description="Detailed description of the labeling job. It will be displayed to annotators when they start labeling.",
        content=lj_description_readme_editor,
    )

    lj_description_markdown_support_text = Text(
        (
            "Markdown supported. Learn more "
            "<a href='https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax' target='_blank'>about markdown</a>"
        ),
        "text",
        font_size=get_text_font_size(),
    )

    lj_description_save_btn = create_save_btn()
    lj_description_sidebar_container = Container(
        [
            lj_description_title_field,
            lj_description_description_field,
            lj_description_readme_field,
            lj_description_markdown_support_text,
            lj_description_save_btn,
        ]
    )
    # ----------------------------

    # LAYOUT
    lj_description_edit_text = Text("Job Info", status="text", font_size=get_text_font_size())
    lj_description_edit_btn = Button(
        text="EDIT",
        icon="zmdi zmdi-edit",
        button_type="text",
        button_size="small",
        emit_on_click="openSidebar",
        style=get_set_settings_button_style(),
    )

    lj_description_container = get_set_settings_container(
        lj_description_edit_text, lj_description_edit_btn
    )
    # ----------------------------

    # PREVIEW
    lj_description_title_preview = Text("Title:", "text", font_size=get_text_font_size())
    # ----------------------------

    return (
        # sidebar
        lj_description_title_input,
        lj_description_description_editor,
        lj_description_readme_editor,
        lj_description_save_btn,
        lj_description_sidebar_container,
        # preview
        lj_description_title_preview,
        # layout
        lj_description_container,
    )
