import os
from typing import Literal
from supervisely.app.widgets import (
    Input,
    Text,
    Select,
    RadioGroup,
    RadioTable,
    Button,
    Container,
    Field,
    RadioTabs,
    TrainedModelsSelector,
    OneOf,
    Checkbox,
)
from supervisely.io.json import load_json_file

# from supervisely.api.agent_api import AgentInfo
import src.globals as g
from src.ui.dtl.utils import (
    get_text_font_size,
    create_save_btn,
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
)
import src.ui.dtl.actions.deploy_yolov8.layout.utils as utils


COL_ID = "task id".upper()
COL_PROJECT = "training data project".upper()
COL_ARTIFACTS = "artifacts".upper()
COL_PREVIEW = "preview".upper()

columns = [
    COL_ID,
    COL_PROJECT,
    COL_ARTIFACTS,
    COL_PREVIEW,
]


models_dir = os.path.join("src", "ui", "dtl", "actions", "deploy_yolov8", "models")
det_models_data_path = os.path.join(models_dir, "det_models_data.json")
seg_models_data_path = os.path.join(models_dir, "seg_models_data.json")
pose_models_data_path = os.path.join(models_dir, "pose_models_data.json")
det_models_data = load_json_file(det_models_data_path)
seg_models_data = load_json_file(seg_models_data_path)
pose_models_data = load_json_file(pose_models_data_path)

TASK_TYPES_MODELS_INFO_MAP = {
    "object detection": det_models_data,
    "instance segmentation": seg_models_data,
    "pose estimation": pose_models_data,
}


def get_pretrained_model_table_rows(
    table: RadioTable,
    task_type: Literal["object detection", "instance segmentation", "pose estimation"],
):
    models_data = TASK_TYPES_MODELS_INFO_MAP[task_type]
    models_table_columns = [key for key in models_data[0].keys()]
    models_table_subtitles = [None] * len(models_table_columns)
    models_table_rows = []
    for element in models_data:
        models_table_rows.append(list(element.values()))
    table.set_data(
        columns=models_table_columns,
        rows=models_table_rows,
        subtitles=models_table_subtitles,
    )


def create_model_selector_widgets():
    # SIDEBAR

    # CUSTOM MODEL OPTION SUPERVISELY
    remote_path_to_custom_models = "/yolov8_train/"

    model_selector_sidebar_custom_model_table_detection = TrainedModelsSelector(
        team_id=g.TEAM_ID,
        training_app_directory=remote_path_to_custom_models,
        task_type="object detection",
    )

    model_selector_sidebar_custom_model_table_segmentation = TrainedModelsSelector(
        team_id=g.TEAM_ID,
        training_app_directory=remote_path_to_custom_models,
        task_type="instance segmentation",
    )

    model_selector_sidebar_custom_model_table_pose_estimation = TrainedModelsSelector(
        team_id=g.TEAM_ID,
        training_app_directory=remote_path_to_custom_models,
        task_type="pose estimation",
    )
    # ------------------------------

    # CUSTOM MODEL OPTION INPUT
    model_selector_sidebar_custom_model_input = Input(placeholder="Enter path to model checkpoint")
    model_selector_sidebar_custom_model_input_field = Field(
        title="Path to checkpoint",
        description="Enter path to model checkpoint from Team Files",
        content=model_selector_sidebar_custom_model_input,
    )

    # PUBLIC MODEL OPTIONS
    model_selector_sidebar_public_model_table_detection = RadioTable(columns=[], rows=[])
    get_pretrained_model_table_rows(
        model_selector_sidebar_public_model_table_detection, task_type="object detection"
    )

    model_selector_sidebar_public_model_table_segmentation = RadioTable(columns=[], rows=[])
    get_pretrained_model_table_rows(
        model_selector_sidebar_public_model_table_segmentation, task_type="instance segmentation"
    )

    model_selector_sidebar_public_model_table_pose_estimation = RadioTable(columns=[], rows=[])
    get_pretrained_model_table_rows(
        model_selector_sidebar_public_model_table_pose_estimation, task_type="pose estimation"
    )
    # ------------------------------

    # TASK TYPE SELECTOR CUSTOM
    model_selector_sidebar_task_type_selector_items_custom = [
        RadioGroup.Item(
            value="object detection",
            label="Object Detection",
            content=model_selector_sidebar_custom_model_table_detection,
        ),
        RadioGroup.Item(
            value="instance segmentation",
            label="Instance Segmentation",
            content=model_selector_sidebar_custom_model_table_segmentation,
        ),
        RadioGroup.Item(
            value="pose estimation",
            label="Pose Estimation",
            content=model_selector_sidebar_custom_model_table_pose_estimation,
        ),
    ]

    model_selector_sidebar_task_type_selector_custom = RadioGroup(
        items=model_selector_sidebar_task_type_selector_items_custom, direction="vertical"
    )

    model_selector_sidebar_task_type_selector_oneof_custom = OneOf(
        model_selector_sidebar_task_type_selector_custom
    )

    model_selector_sidebar_custom_task_type_selector_container = Container(
        [
            model_selector_sidebar_task_type_selector_custom,
            model_selector_sidebar_task_type_selector_oneof_custom,
        ]
    )
    # ------------------------------

    # TASK TYPE SELECTOR PUBLIC
    model_selector_sidebar_task_type_selector_items_public = [
        RadioGroup.Item(
            value="object detection",
            label="Object Detection",
            content=model_selector_sidebar_public_model_table_detection,
        ),
        RadioGroup.Item(
            value="instance segmentation",
            label="Instance Segmentation",
            content=model_selector_sidebar_public_model_table_segmentation,
        ),
        RadioGroup.Item(
            value="pose estimation",
            label="Pose Estimation",
            content=model_selector_sidebar_public_model_table_pose_estimation,
        ),
    ]

    model_selector_sidebar_task_type_selector_public = RadioGroup(
        items=model_selector_sidebar_task_type_selector_items_public, direction="vertical"
    )

    model_selector_sidebar_task_type_selector_oneof_public = OneOf(
        model_selector_sidebar_task_type_selector_public
    )

    model_selector_sidebar_public_task_type_selector_container = Container(
        [
            model_selector_sidebar_task_type_selector_public,
            model_selector_sidebar_task_type_selector_oneof_public,
        ]
    )

    # CUSTOM MODEL OPTION
    model_selector_sidebar_custom_model_option_items = [
        Select.Item(
            value="table",
            label="Select trained model (that you trained in Supervisely)",
            content=model_selector_sidebar_custom_task_type_selector_container,
        ),
        Select.Item(
            value="checkpoint",
            label="Custom checkpoint directory",
            content=model_selector_sidebar_custom_model_input_field,
        ),
    ]
    model_selector_sidebar_custom_model_option_selector = Select(
        model_selector_sidebar_custom_model_option_items
    )
    model_selector_sidebar_custom_model_option_oneof = OneOf(
        model_selector_sidebar_custom_model_option_selector
    )
    model_selector_sidebar_custom_model_option_container = Container(
        [
            model_selector_sidebar_custom_model_option_selector,
            model_selector_sidebar_custom_model_option_oneof,
        ]
    )

    model_selector_sidebar_custom_model_option_field = Field(
        title="Custom model",
        description="Select whether you want to use a model trained in Supervisely or a custom checkpoint directory",
        content=model_selector_sidebar_custom_model_option_container,
    )

    # CUSTOM /PUBLIC TABS
    model_selector_sidebar_model_type_tabs = RadioTabs(
        titles=["Custom models", "Pretrained public models"],
        descriptions=["Models trained by you", "Models trained by YOLOV8 team"],
        contents=[
            model_selector_sidebar_custom_model_option_field,
            model_selector_sidebar_public_task_type_selector_container,
        ],
    )

    # SIDEBAR CONTAINER
    model_selector_sidebar_save_btn = create_save_btn()
    model_selector_sidebar_container = Container(
        [
            model_selector_sidebar_model_type_tabs,
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
        Text("Auto stop model on pipeline finish", "text", font_size=13), False
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

    utils.set_default_model(
        model_selector_sidebar_custom_model_table_detection,
        model_selector_sidebar_custom_model_table_segmentation,
        model_selector_sidebar_custom_model_table_pose_estimation,
        model_selector_sidebar_model_type_tabs,
        model_selector_sidebar_task_type_selector_custom,
    )

    return (
        # sidebar
        # custom options
        model_selector_sidebar_custom_model_table_detection,
        model_selector_sidebar_custom_model_table_segmentation,
        model_selector_sidebar_custom_model_table_pose_estimation,
        model_selector_sidebar_custom_model_input,
        model_selector_sidebar_custom_model_option_selector,
        model_selector_sidebar_task_type_selector_custom,
        # public options
        model_selector_sidebar_public_model_table_detection,
        model_selector_sidebar_public_model_table_segmentation,
        model_selector_sidebar_public_model_table_pose_estimation,
        model_selector_sidebar_task_type_selector_public,
        # sidebar
        model_selector_sidebar_model_type_tabs,
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
