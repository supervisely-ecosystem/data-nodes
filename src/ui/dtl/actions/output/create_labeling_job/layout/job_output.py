from src.ui.dtl.utils import (
    create_save_btn,
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
)
from supervisely.app.widgets import Button, Container, Text, Input, Field, Checkbox, NotificationBox


def create_job_output_widgets():
    # SIDEBAR SETTINGS
    lj_output_project_name_input = Input(placeholder="Enter project name", size="small")
    lj_output_project_name_field = Field(
        title="Project Name",
        description="Project with given name will be created in your workspace and labeling job will be assigned to it",
        content=lj_output_project_name_input,
    )

    lj_output_dataset_keep_checkbox = Checkbox("Keep original datasets structure", checked=False)
    lj_output_dataset_name_input = Input(placeholder="Enter dataset name", size="small")
    lj_output_dataset_container = Container(
        [lj_output_dataset_keep_checkbox, lj_output_dataset_name_input]
    )
    lj_output_dataset_name_field = Field(
        title="Dataset Name",
        description=(
            "Dataset with given name will be created in the project. "
            "If you want to use dataset name from input project or "
            "dataset from 'Dataset' layer "
            "check the 'Keep original datasets structure' checkbox below"
        ),
        content=lj_output_dataset_container,
    )

    lj_output_save_btn = create_save_btn()
    lj_output_sidebar_container = Container(
        [lj_output_project_name_field, lj_output_dataset_name_field, lj_output_save_btn]
    )
    # ----------------------------

    # PREVIEW
    lj_output_project_name_preview = Text("Project name:", "text", font_size=get_text_font_size())
    lj_output_dataset_name_preview = Text("Dataset name:", "text", font_size=get_text_font_size())
    lj_output_modifies_data_preview = NotificationBox(
        title="Labeling job will be created for input project",
        description="Layers that modify data not found, labeling job will be created for input project",
        box_type="info",
    )
    lj_output_modifies_data_preview.hide()

    # lj_output_modifies_data_preview = Text(
    #     "Layers that modify data not found, labeling job will be created for input project.",
    #     "text",
    #     font_size=get_text_font_size(),
    # )
    lj_output_container_preview = Container(
        [
            lj_output_project_name_preview,
            lj_output_dataset_name_preview,
            lj_output_modifies_data_preview,
        ]
    )
    # ----------------------------

    # LAYOUT
    lj_output_text = Text("Output", status="text", font_size=get_text_font_size())
    lj_output_edit_btn = Button(
        text="EDIT",
        icon="zmdi zmdi-folder",
        button_type="text",
        button_size="small",
        emit_on_click="openSidebar",
        style=get_set_settings_button_style(),
    )

    lj_output_edit_container = get_set_settings_container(lj_output_text, lj_output_edit_btn)
    # ----------------------------

    return (
        # sidebar
        lj_output_project_name_input,
        lj_output_dataset_keep_checkbox,
        lj_output_dataset_name_input,
        lj_output_save_btn,
        lj_output_sidebar_container,
        # preview
        lj_output_project_name_preview,
        lj_output_dataset_name_preview,
        lj_output_container_preview,
        lj_output_modifies_data_preview,
        # layout
        lj_output_edit_btn,
        lj_output_edit_container,
    )
