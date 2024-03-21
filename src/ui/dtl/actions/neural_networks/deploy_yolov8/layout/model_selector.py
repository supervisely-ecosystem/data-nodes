import os
from typing import Literal
from supervisely.app.widgets import (
    Text,
    RadioTable,
    Button,
    Container,
    RadioTabs,
    CustomModelsSelector,
    PretrainedModelsSelector,
    Checkbox,
)
from supervisely.io.json import load_json_file
from supervisely.nn.checkpoints import yolov8

import src.globals as g
from src.ui.dtl.utils import (
    get_text_font_size,
    create_save_btn,
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
)
import src.ui.dtl.actions.neural_networks.deploy_yolov8.layout.utils as utils
from src.ui.dtl.actions.neural_networks.deploy_yolov8.layout.models import (
    models as pretrained_models,
)


def create_model_selector_widgets():
    # SIDEBAR

    # CUSTOM MODEL OPTION SUPERVISELY
    custom_models = yolov8.get_list(g.api, g.TEAM_ID)
    model_selector_sidebar_custom_model_table = CustomModelsSelector(
        g.TEAM_ID,
        custom_models,
        True,
        ["object_detection", "instance segmentation", "pose estimation"],
    )

    custom_models_task_types = model_selector_sidebar_custom_model_table.get_available_task_types()
    if "object detection" in custom_models_task_types:
        model_selector_sidebar_custom_model_table.set_active_task_type("object detection")
    # ------------------------------

    # PUBLIC MODEL OPTIONS
    model_selector_sidebar_public_model_table = PretrainedModelsSelector(pretrained_models)
    model_selector_sidebar_public_model_table.set_active_task_type("object detection")
    # ------------------------------

    # CUSTOM /PUBLIC TABS
    model_selector_sidebar_model_source_tabs = RadioTabs(
        titles=["Custom models", "Pretrained public models"],
        descriptions=["Models trained by you", "Models trained by YOLOV8 team"],
        contents=[
            model_selector_sidebar_custom_model_table,
            model_selector_sidebar_public_model_table,
        ],
    )
    if len(custom_models) == 0:
        model_selector_sidebar_model_source_tabs.set_active_tab("Pretrained public models")

    # SIDEBAR CONTAINER
    model_selector_sidebar_save_btn = create_save_btn()
    model_selector_sidebar_container = Container(
        [
            model_selector_sidebar_model_source_tabs,
            model_selector_sidebar_save_btn,
        ]
    )
    # ------------------------------

    # PREVIEW
    # TODO: App thumbnail widget
    model_selector_preview = Text("Checkpoint:", status="text", font_size=get_text_font_size())
    model_selector_preview.hide()
    model_selector_preview_type = Text("Type:", status="text", font_size=get_text_font_size())
    model_selector_preview_type.hide()
    # ------------------------------

    # LAYOUT
    # STOP MODEL AFTER INFERENCE
    model_selector_stop_model_after_pipeline_checkbox = Checkbox(
        Text("Auto stop model on pipeline finish", "text", font_size=13), True
    )

    model_selector_layout_edit_text = Text(
        "Select model", status="text", font_size=get_text_font_size()
    )
    model_selector_layout_edit_btn = Button(
        text="EDIT",
        icon="zmdi zmdi-edit",
        button_type="text",
        button_size="small",
        emit_on_click="openSidebar",
        style=get_set_settings_button_style(),
    )

    model_selector_layout_container = get_set_settings_container(
        model_selector_layout_edit_text, model_selector_layout_edit_btn
    )
    # ------------------------------

    return (
        # sidebar
        # custom options
        model_selector_sidebar_custom_model_table,
        # public options
        model_selector_sidebar_public_model_table,
        # sidebar
        model_selector_sidebar_model_source_tabs,
        model_selector_sidebar_save_btn,
        model_selector_sidebar_container,
        # preview
        model_selector_preview,
        model_selector_preview_type,
        # layout
        model_selector_layout_edit_text,
        model_selector_layout_edit_btn,
        model_selector_layout_container,
        model_selector_stop_model_after_pipeline_checkbox,
    )
