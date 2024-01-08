from typing import List, NamedTuple
from supervisely.api.api import Api
from supervisely.app.widgets import (
    Input,
    Button,
    Text,
    Select,
    RadioTable,
    RadioTabs,
    RadioGroup,
    TrainedModelsSelector,
    Checkbox,
)

from supervisely.api.app_api import SessionInfo
from supervisely.io.fs import get_file_name_with_ext
import src.globals as g


def set_agent_selector_preview(
    agent_selector_sidebar_selector: Select,
    agent_selector_sidebar_device_selector: Select,
    agent_selector_preview: Text,
):
    icon = "<i class='zmdi zmdi-memory'></i>"
    agent_id = agent_selector_sidebar_selector.get_value()
    agent_name = g.api.agent.get_info_by_id(agent_id).name
    device = agent_selector_sidebar_device_selector.get_label()
    agent_selector_preview.set(f"{icon} {agent_name} ({device})", "text")
    agent_selector_preview.show()


def set_model_selector_preview(
    settings: dict,
    model_selector_preview: Text,
    model_selector_preview_type: Text,
):
    if settings["model_type"] == "Pretrained models":
        model_type = "Pretrained"
    elif settings["model_type"] == "Custom models":
        model_type = "Custom"

    model_selector_preview.set(f"Checkpoint: {settings['model_name']}", "text")
    model_selector_preview_type.set(f"Type: {model_type}", "text")
    model_selector_preview.show()
    model_selector_preview_type.show()


def set_model_serve_preview(message: str, model_serve_preview: Text, status="text"):
    model_serve_preview.set(message, status)


def save_agent_settings(
    saved_settings: dict,
    agent_selector_sidebar_selector: Select,
    agent_selector_sidebar_device_selector: Select,
):
    saved_settings["agent_id"] = agent_selector_sidebar_selector.get_value()
    saved_settings["device"] = agent_selector_sidebar_device_selector.get_value()
    return saved_settings


def save_model_settings(
    settings: dict,
    model_selector_sidebar_model_type_tabs: RadioTabs,
    model_selector_sidebar_task_type_selector_public: RadioGroup,
    model_selector_sidebar_public_model_table_detection: RadioTable,
    model_selector_sidebar_public_model_table_segmentation: RadioTable,
    model_selector_sidebar_public_model_table_pose_estimation: RadioTable,
    model_selector_sidebar_custom_model_option_selector: Select,
    model_selector_sidebar_custom_model_input: Input,
    model_selector_sidebar_task_type_selector_custom: RadioGroup,
    model_selector_sidebar_custom_model_table_detection: TrainedModelsSelector,
    model_selector_sidebar_custom_model_table_segmentation: TrainedModelsSelector,
    model_selector_sidebar_custom_model_table_pose_estimation: TrainedModelsSelector,
    model_selector_stop_model_after_pipeline_checkbox: Checkbox,
):
    # init default
    model_type = None
    model_name = None
    task_type = None
    model_path = None
    stop_model_session = True

    # MODEL SELECTOR
    model_type = model_selector_sidebar_model_type_tabs.get_active_tab()
    if model_type == "Pretrained public models":
        model_type = "Pretrained models"
        task_type = model_selector_sidebar_task_type_selector_public.get_value()
        if task_type == "object detection":
            model_name = model_selector_sidebar_public_model_table_detection.get_selected_row()[0]
        elif task_type == "instance segmentation":
            model_name = model_selector_sidebar_public_model_table_segmentation.get_selected_row()[
                0
            ]
        elif task_type == "pose estimation":
            model_name = (
                model_selector_sidebar_public_model_table_pose_estimation.get_selected_row()[0]
            )

    elif model_type == "Custom models":
        model_type = "Custom models"
        custom_model_option = model_selector_sidebar_custom_model_option_selector.get_value()
        if custom_model_option == "checkpoint":
            model_path = model_selector_sidebar_custom_model_input.get_value()
            model_name = get_file_name_with_ext(model_path)
        elif custom_model_option == "table":
            task_type = model_selector_sidebar_task_type_selector_custom.get_value()
            if task_type == "object detection":
                selected_row: TrainedModelsSelector.ModelRow = (
                    model_selector_sidebar_custom_model_table_detection.get_selected_row()
                )
                if selected_row is not None:
                    model_path = selected_row.artifacts_selector.get_value()
                    model_name = selected_row.artifacts_selector.get_label()
            elif task_type == "instance segmentation":
                selected_row: TrainedModelsSelector.ModelRow = (
                    model_selector_sidebar_custom_model_table_segmentation.get_selected_row()
                )
                if selected_row is not None:
                    model_path = selected_row.artifacts_selector.get_value()
                    model_name = selected_row.artifacts_selector.get_label()
            elif task_type == "pose estimation":
                selected_row: TrainedModelsSelector.ModelRow = (
                    model_selector_sidebar_custom_model_table_pose_estimation.get_selected_row()
                )
                if selected_row is not None:
                    model_path = selected_row.artifacts_selector.get_value()
                    model_name = selected_row.artifacts_selector.get_label()

    stop_model_session = model_selector_stop_model_after_pipeline_checkbox.is_checked()

    settings["model_type"] = model_type
    settings["model_name"] = model_name
    settings["task_type"] = task_type
    settings["model_path"] = model_path
    settings["stop_model_session"] = stop_model_session
    return settings


def save_model_serve_settings(settings: dict, task_id: int):
    settings["session_id"] = task_id
    return settings


def save_settings(
    settings: dict,
    agent_selector_sidebar_selector: Select,
    agent_selector_sidebar_device_selector: Select,
    model_selector_sidebar_model_type_tabs: RadioTabs,
    model_selector_sidebar_task_type_selector_public: RadioGroup,
    model_selector_sidebar_public_model_table_detection: RadioTable,
    model_selector_sidebar_public_model_table_segmentation: RadioTable,
    model_selector_sidebar_public_model_table_pose_estimation: RadioTable,
    model_selector_sidebar_custom_model_option_selector: Select,
    model_selector_sidebar_custom_model_input: Input,
    model_selector_sidebar_task_type_selector_custom: RadioGroup,
    model_selector_sidebar_custom_model_table_detection: TrainedModelsSelector,
    model_selector_sidebar_custom_model_table_segmentation: TrainedModelsSelector,
    model_selector_sidebar_custom_model_table_pose_estimation: TrainedModelsSelector,
    model_selector_stop_model_after_pipeline_checkbox: Checkbox,
):
    settings = save_agent_settings(
        settings, agent_selector_sidebar_selector, agent_selector_sidebar_device_selector
    )
    settings = save_model_settings(
        settings,
        model_selector_sidebar_model_type_tabs,
        model_selector_sidebar_task_type_selector_public,
        model_selector_sidebar_public_model_table_detection,
        model_selector_sidebar_public_model_table_segmentation,
        model_selector_sidebar_public_model_table_pose_estimation,
        model_selector_sidebar_custom_model_option_selector,
        model_selector_sidebar_custom_model_input,
        model_selector_sidebar_task_type_selector_custom,
        model_selector_sidebar_custom_model_table_detection,
        model_selector_sidebar_custom_model_table_segmentation,
        model_selector_sidebar_custom_model_table_pose_estimation,
        model_selector_stop_model_after_pipeline_checkbox,
    )
    return settings


def validate_settings(
    settings: dict,
    model_serve_preview: Text,
    model_selector_sidebar_custom_model_option_selector: Select,
) -> bool:
    if settings.get("agent_id", None) is None:
        set_model_serve_preview("Please select agent", model_serve_preview, "warning")
        return False
    if settings.get("device", None) is None:
        set_model_serve_preview("Please select device", model_serve_preview, "warning")
        return False
    if (
        settings.get("model_type", None) is None
        or settings.get("model_name", None) is None
        or settings.get("task_type", None) is None
    ):
        set_model_serve_preview("Please select model", model_serve_preview, "warning")
        return False

    if model_selector_sidebar_custom_model_option_selector.get_value() == "checkpoint":
        if settings.get("model_path", None) is None or settings.get("model_path", None) == "":
            set_model_serve_preview("Please enter model path", model_serve_preview, "warning")
            return False
    return True


# OTHER
def get_agent_devices(agent_info: NamedTuple) -> List[Select.Item]:
    agent_selector_sidebar_device_selector_items = []
    has_gpu = agent_info.capabilities["types"]["app_gpu"]["enabled"]
    if has_gpu:
        agent_selector_sidebar_device_selector_items.append(
            Select.Item(value="cuda:0", label="GPU")
        )
    agent_selector_sidebar_device_selector_items.append(Select.Item(value="cpu", label="CPU"))
    return agent_selector_sidebar_device_selector_items


def start_app(api: Api, workspace_id: int, saved_settings: dict) -> SessionInfo:
    session_info = api.app.start(
        agent_id=saved_settings["agent_id"],
        module_id=500,
        workspace_id=workspace_id,
        description=f"AutoServe session for Serve YOLOv8",
        task_name="AutoServe/serve",
        params=saved_settings,
        app_version="data-nodes-deploy-yolov8",
        is_branch=True,
    )
    return session_info


def deploy_model(api: Api, session_id: int, saved_settings: dict):
    api.task.send_request(
        session_id,
        "deploy_nn_serving",
        data={
            "device": saved_settings[
                "device"
            ],  # "cpu" / "cuda" / "cuda:0" / "cuda:1" / "cuda:2" / "cuda:3"
            "model_dir": "data-nodes/models",  # downloaded models save path
            "deploy_params": {
                "model_source": saved_settings[
                    "model_type"
                ],  # "Pretrained models" / "Custom models"
                "weights_name": saved_settings["model_name"],
                "custom_weights_path": saved_settings[
                    "model_path"
                ],  # "path_to_file_in_team_files", # None,
                "task_type": saved_settings[
                    "task_type"
                ],  # "object detection" / "instance segmentation" / "pose estimation"
            },
        },
    )


# Check model


def check_model_avaliability_by_task_type(
    task_type: str,
    model_selector_sidebar_custom_model_table_segmentation: TrainedModelsSelector,
    model_selector_sidebar_custom_model_table_detection: TrainedModelsSelector,
    model_selector_sidebar_custom_model_table_pose_estimation: TrainedModelsSelector,
    model_selector_sidebar_save_btn: Button,
):
    if task_type == "object detection":
        if len(model_selector_sidebar_custom_model_table_segmentation.rows) == 0:
            model_selector_sidebar_save_btn.disable()
        else:
            model_selector_sidebar_save_btn.enable()
    if task_type == "instance segmentation":
        if len(model_selector_sidebar_custom_model_table_detection.rows) == 0:
            model_selector_sidebar_save_btn.disable()
        else:
            model_selector_sidebar_save_btn.enable()
    if task_type == "pose estimation":
        if len(model_selector_sidebar_custom_model_table_pose_estimation.rows) == 0:
            model_selector_sidebar_save_btn.disable()
        else:
            model_selector_sidebar_save_btn.enable()


def check_model_avaliability_by_model_type(
    model_type: str,
    model_selector_sidebar_custom_model_option_selector: Select,
    model_selector_sidebar_custom_model_table_segmentation: TrainedModelsSelector,
    model_selector_sidebar_custom_model_table_detection: TrainedModelsSelector,
    model_selector_sidebar_custom_model_table_pose_estimation: TrainedModelsSelector,
    model_selector_sidebar_save_btn: Button,
):
    if model_type == "Custom models":
        if model_selector_sidebar_custom_model_option_selector.get_value() == "table":
            if (
                len(model_selector_sidebar_custom_model_table_detection.rows) == 0
                and len(model_selector_sidebar_custom_model_table_segmentation.rows) == 0
                and len(model_selector_sidebar_custom_model_table_pose_estimation.rows) == 0
            ):
                model_selector_sidebar_save_btn.disable()
            else:  # if at least one table is not empty
                model_selector_sidebar_save_btn.enable()
        else:
            model_selector_sidebar_save_btn.enable()
    else:
        model_selector_sidebar_save_btn.enable()


def set_default_model(
    model_selector_sidebar_custom_model_table_detection: TrainedModelsSelector,
    model_selector_sidebar_custom_model_table_segmentation: TrainedModelsSelector,
    model_selector_sidebar_custom_model_table_pose_estimation: TrainedModelsSelector,
    model_selector_sidebar_model_type_tabs: RadioTabs,
    model_selector_sidebar_task_type_selector_custom: RadioGroup,
):
    if (
        len(model_selector_sidebar_custom_model_table_detection.rows) == 0
        and len(model_selector_sidebar_custom_model_table_segmentation.rows) == 0
        and len(model_selector_sidebar_custom_model_table_pose_estimation.rows) == 0
    ):
        model_selector_sidebar_model_type_tabs.set_active_tab("Pretrained public models")
    elif (
        len(model_selector_sidebar_custom_model_table_detection.rows) > 0
        and len(model_selector_sidebar_custom_model_table_segmentation.rows) == 0
        and len(model_selector_sidebar_custom_model_table_pose_estimation.rows) == 0
    ):
        model_selector_sidebar_task_type_selector_custom.set_value("object detection")
    elif (
        len(model_selector_sidebar_custom_model_table_detection.rows) == 0
        and len(model_selector_sidebar_custom_model_table_segmentation.rows) > 0
        and len(model_selector_sidebar_custom_model_table_pose_estimation.rows) == 0
    ):
        model_selector_sidebar_task_type_selector_custom.set_value("instance segmentation")
    elif (
        len(model_selector_sidebar_custom_model_table_detection.rows) == 0
        and len(model_selector_sidebar_custom_model_table_segmentation.rows) > 0
        and len(model_selector_sidebar_custom_model_table_pose_estimation.rows) == 0
    ):
        model_selector_sidebar_task_type_selector_custom.set_value("pose estimation")
