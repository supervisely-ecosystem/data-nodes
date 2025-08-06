from os.path import join
from typing import List

from supervisely.api.agent_api import AgentInfo
from supervisely.api.api import Api
from supervisely.api.app_api import SessionInfo
from supervisely.app.widgets import (
    AgentSelector,
    Button,
    Checkbox,
    ExperimentSelector,
    PretrainedModelsSelector,
    RadioGroup,
    RadioTabs,
    Select,
    Text,
)
from supervisely.io.fs import get_file_name_with_ext
from supervisely.nn.utils import ModelSource

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
    train_version: str = "v1",
):
    if settings["model_source"] == ModelSource.PRETRAINED:
        model_source = "Pretrained"
    elif settings["model_source"] == ModelSource.CUSTOM:
        model_source = "Custom"

    if train_version == "v1":
        checkpoint_name = settings["checkpoint_name"]
    elif train_version == "v2":
        checkpoint_name = get_file_name_with_ext(
            settings["model_params"]["model_files"]["checkpoint"]
        )

    model_selector_preview.set(f"Checkpoint: {checkpoint_name}", "text")
    model_selector_preview_type.set(f"Type: {model_source}", "text")
    model_selector_preview.show()
    model_selector_preview_type.show()


def set_model_serve_preview(message: str, model_serve_preview: Text, status="text"):
    model_serve_preview.set(message, status)


def save_agent_settings(
    saved_settings: dict,
    agent_selector_sidebar_selector: AgentSelector,
    agent_selector_sidebar_device_selector: Select,
):
    saved_settings["agent_id"] = agent_selector_sidebar_selector.get_value()
    saved_settings["device"] = agent_selector_sidebar_device_selector.get_value()
    return saved_settings


def save_model_settings(
    settings: dict,
    model_selector_sidebar_model_source_tabs: RadioGroup,
    model_selector_sidebar_public_model_table: PretrainedModelsSelector,
    model_selector_runtime_selector_sidebar: Select,
    model_selector_sidebar_custom_model_table: ExperimentSelector,
    model_selector_stop_model_after_pipeline_checkbox: Checkbox,
    train_version: str = "v1",
):
    from supervisely.nn import ExperimentInfo

    model_params = {}
    # MODEL SELECTOR
    model_source = model_selector_sidebar_model_source_tabs.get_active_tab()
    if model_source == ModelSource.PRETRAINED:
        model_params = model_selector_sidebar_public_model_table.get_selected_model_params(
            train_version=train_version
        )

    elif model_source == ModelSource.CUSTOM:
        selected_checkpoint = (
            model_selector_sidebar_custom_model_table.get_selected_checkpoint_name()
        )
        if selected_checkpoint is None:
            raise RuntimeError("Please, select a model before saving it.")
        experiment_info: ExperimentInfo = (
            model_selector_sidebar_custom_model_table.get_selected_experiment_info()
        )
        if train_version == "v1":
            model_params = {
                "task_type": experiment_info.task_type,
                "checkpoint_name": get_file_name_with_ext(selected_checkpoint),
                "checkpoint_url": selected_checkpoint,
            }
            model_files = experiment_info.model_files
            config = model_files.get("config")
            if config is not None:
                model_params["config_url"] = join(experiment_info.artifacts_dir, config.strip("/"))
        elif train_version == "v2":
            model_params = model_selector_sidebar_custom_model_table.get_deploy_params()

    stop_model_session = model_selector_stop_model_after_pipeline_checkbox.is_checked()

    # common
    settings["model_source"] = model_source
    settings["task_type"] = model_params.get("task_type", None)
    settings["checkpoint_name"] = model_params.get("checkpoint_name", None)
    settings["checkpoint_url"] = model_params.get("checkpoint_url", None)
    settings["stop_model_session"] = stop_model_session

    # specific
    config_url = model_params.get("config_url", None)
    if config_url is not None:
        settings["config_url"] = config_url
    arch_type = model_params.get("arch_type", None)
    if arch_type is not None:
        settings["arch_type"] = arch_type
    runtime = model_selector_runtime_selector_sidebar.get_value()
    if runtime is not None:
        settings["runtime"] = runtime
    if train_version == "v2":
        settings["model_params"] = model_params
    return settings


def save_model_serve_settings(settings: dict, task_id: int):
    settings["session_id"] = task_id
    return settings


def save_settings(
    settings: dict,
    agent_selector_sidebar_selector: AgentSelector,
    agent_selector_sidebar_device_selector: Select,
    model_selector_sidebar_model_source_tabs: RadioTabs,
    model_selector_sidebar_public_model_table: PretrainedModelsSelector,
    model_selector_runtime_selector_sidebar: Select,
    model_selector_sidebar_custom_model_table: ExperimentSelector,
    model_selector_stop_model_after_pipeline_checkbox: Checkbox,
    train_version: str = "v1",
):
    settings = save_agent_settings(
        settings, agent_selector_sidebar_selector, agent_selector_sidebar_device_selector
    )
    settings = save_model_settings(
        settings,
        model_selector_sidebar_model_source_tabs,
        model_selector_sidebar_public_model_table,
        model_selector_runtime_selector_sidebar,
        model_selector_sidebar_custom_model_table,
        model_selector_stop_model_after_pipeline_checkbox,
        train_version,
    )
    return settings


def validate_settings(
    settings: dict,
    model_serve_preview: Text,
    train_version: str = "v2",
) -> bool:
    if train_version == "v1":
        if settings.get("agent_id", None) is None:
            set_model_serve_preview("Please select agent", model_serve_preview, "warning")
            return False
        if settings.get("device", None) is None:
            set_model_serve_preview("Please select device", model_serve_preview, "warning")
            return False
        if (
            settings.get("model_source", None) is None
            or settings.get("checkpoint_name", None) is None
            or settings.get("task_type", None) is None
        ):
            set_model_serve_preview("Please select model", model_serve_preview, "warning")
            return False
    elif train_version == "v2":
        model_params = settings.get("model_params", None)
        if model_params is None:
            set_model_serve_preview("Please select model", model_serve_preview, "warning")
            return False
    return True


# OTHER
def get_agent_devices(agent_info: AgentInfo) -> List[Select.Item]:
    agent_selector_sidebar_device_selector_items = []
    has_gpu = False
    gpu_info = agent_info.gpu_info
    if gpu_info is not None:
        has_gpu = agent_info.gpu_info.get("is_available", False)
    if has_gpu:
        for idx, device_name in enumerate(agent_info.gpu_info["device_names"]):
            agent_selector_sidebar_device_selector_items.append(
                Select.Item(value=f"cuda:{idx}", label=device_name)
            )
    agent_selector_sidebar_device_selector_items.append(Select.Item(value="cpu", label="CPU"))
    return agent_selector_sidebar_device_selector_items


def start_app(
    api: Api,
    workspace_id: int,
    saved_settings: dict,
    framework_name: str,
    slug: str,
) -> SessionInfo:
    module_id = api.app.get_ecosystem_module_id(slug)
    app_params = {
        "agent_id": saved_settings["agent_id"],
        # "app_id": 0,
        "module_id": module_id,
        "workspace_id": workspace_id,
        "description": f"AutoServe session for Serve {framework_name}",
        "task_name": "AutoServe/serve",
        "params": {"autostart": False, **saved_settings},
        "app_version": None,
        "is_branch": False,
    }
    session_info = api.app.start(**app_params)
    return session_info


def deploy_model(api: Api, session_id: int, saved_settings: dict, train_version: str = "v1"):
    deploy_params = {}
    # common
    if train_version == "v1":
        deploy_params["device"] = saved_settings["device"]
        deploy_params["model_source"] = saved_settings["model_source"]
        deploy_params["checkpoint_name"] = saved_settings["checkpoint_name"]
        deploy_params["checkpoint_url"] = saved_settings["checkpoint_url"]
        deploy_params["task_type"] = saved_settings["task_type"]
        # specific
        config_url = saved_settings.get("config_url", None)
        if config_url is not None:
            deploy_params["config_url"] = config_url
        arch_type = saved_settings.get("arch_type", None)
        if arch_type is not None:
            deploy_params["arch_type"] = arch_type

    elif train_version == "v2":
        deploy_params = saved_settings["model_params"]
        deploy_params["device"] = saved_settings["device"]

    runtime = saved_settings.get("runtime", None)
    if runtime is not None:
        deploy_params["runtime"] = runtime

    api.task.send_request(session_id, "deploy_from_api", data={"deploy_params": {**deploy_params}})


# Check model
def check_model_avaliability_by_task_type(
    model_selector_sidebar_custom_model_table: ExperimentSelector,
    model_selector_sidebar_save_btn: Button,
):
    if len(model_selector_sidebar_custom_model_table.rows) == 0:
        model_selector_sidebar_save_btn.disable()
    else:
        model_selector_sidebar_save_btn.enable()


def check_model_avaliability_by_model_source(
    model_source: str,
    model_selector_sidebar_custom_model_option_selector: Select,
    model_selector_sidebar_custom_model_table_segmentation: ExperimentSelector,
    model_selector_sidebar_custom_model_table_detection: ExperimentSelector,
    model_selector_sidebar_custom_model_table_pose_estimation: ExperimentSelector,
    model_selector_sidebar_save_btn: Button,
):
    if model_source == ModelSource.CUSTOM:
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
