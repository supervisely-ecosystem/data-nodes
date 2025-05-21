# coding: utf-8
from time import sleep
from typing import List, Tuple, Union

import src.globals as g
from src.compute.dtl_utils.item_descriptor import ImageDescriptor, VideoDescriptor
from src.compute.Layer import Layer
from src.exceptions import BadSettingsError
from supervisely import Annotation, ProjectMeta, VideoAnnotation, logger
from supervisely.nn.inference.session import Session


def wait_model_served(session: Session, wait_attemtps: int = 10, wait_delay_sec: int = 10):
    for _ in range(wait_attemtps):
        is_model_served = session.is_model_deployed()
        if is_model_served:
            return
        else:
            sleep(wait_delay_sec)
            logger.warning("Model is not served yet. Waiting for model to be served")


def check_model_is_deployed(session_id: int, action_name):
    error_message = (
        f"Selected model is not served in '{action_name}' node. "
        "Make sure model is served by visiting app session page: "
        f"<a href='{g.api.server_address}{g.api.app.get_url(session_id)}' target='_blank'>open app</a> "
        "<br>Press the 'SERVE' button if the model is not served and try again. "
        "If the problem persists, try to restart the model or contact support. "
    )

    try:
        session = Session(g.api, session_id)
        is_model_served = session.is_model_deployed()
        if not is_model_served:
            is_model_served = wait_model_served(session, 12)
            if not is_model_served:
                raise TimeoutError(error_message)
    except:
        raise RuntimeError(error_message)


class DeployLayer(Layer):
    action = "deploy"
    title = "Deploy"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": [
                    "session_id",
                    "agent_id",
                    "device",
                    "model_source",
                    "stop_model_session",
                ],
                "properties": {
                    "session_id": {"type": "integer"},
                    "agent_id": {"type": "integer"},
                    "device": {"type": "string"},
                    "model_source": {"type": "string"},
                    "task_type": {"type": "string"},
                    "checkpoint_name": {"type": "string"},
                    "checkpoint_url": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "model_params": {"type": "object"},
                    "runtime": {"type": "string"},
                    "stop_model_session": {"type": "boolean"},
                },
            },
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)
        self.output_meta = ProjectMeta()

    def validate(self):
        settings = self.settings

        if self.net.preview_mode:
            return

        if settings.get("agent_id", None) is None:
            raise BadSettingsError(f"Select agent in '{self.title}' node'")
        if settings.get("device", None) is None:
            raise BadSettingsError(f"Select device in '{self.title}' node")
        if settings.get("model_source", None) is None:
            raise BadSettingsError(f"Select model in '{self.title}' node")
        if not self.net.preview_mode:
            if settings.get("session_id", None) is None:
                raise BadSettingsError(
                    (
                        f"Selected model session is not found. Make sure you have deployed model in '{self.title}' node. "
                        "If you still have problems, try to check model logs for more info or contact support."
                        f"You can also close '{self.title}' node to proceed further with the workflow."
                    )
                )
            check_model_is_deployed(settings["session_id"], self.title)
            super().validate()

    def postprocess(self):
        if self.settings["stop_model_session"]:
            session_id = self.settings["session_id"]
            g.api.app.stop(session_id)
            g.running_sessions_ids.remove(session_id)
            logger.info(f"Session ID: {session_id} has been stopped")
            self.postprocess_cb()

    def process_batch(self, data_els: List[Tuple[ImageDescriptor, Annotation]]):
        yield data_els

    def has_batch_processing(self) -> bool:
        return True


class DeployYOLOv5Layer(DeployLayer):
    action = "deploy_yolo_v5"
    title = "Deploy YOLOv5"


class DeployYOLOv8Layer(DeployLayer):
    action = "deploy_yolo_v8"
    title = "Deploy YOLOv8"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": [
                    "session_id",
                    "agent_id",
                    "device",
                    "model_source",
                    "checkpoint_name",
                    "task_type",
                    "checkpoint_url",
                    "stop_model_session",
                ],
                "properties": {
                    "session_id": {"type": "integer"},
                    "agent_id": {"type": "integer"},
                    "device": {"type": "string"},
                    "model_source": {"type": "string"},
                    "task_type": {"type": "string"},
                    "checkpoint_name": {"type": "string"},
                    "checkpoint_url": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "runtime": {"type": "string"},
                    "stop_model_session": {"type": "boolean"},
                },
            },
        },
    }


class DeployMMDetectionLayer(DeployLayer):
    action = "deploy_mmdetection"
    title = "Deploy MMDetection"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": [
                    "session_id",
                    "agent_id",
                    "device",
                    "model_source",
                    "checkpoint_name",
                    "task_type",
                    "checkpoint_url",
                    "arch_type",
                    "config_url",
                    "stop_model_session",
                ],
                "properties": {
                    "session_id": {"type": "integer"},
                    "agent_id": {"type": "integer"},
                    "device": {"type": "string"},
                    "model_source": {"type": "string"},
                    "task_type": {"type": "string"},
                    "checkpoint_name": {"type": "string"},
                    "checkpoint_url": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "arch_type": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "config_url": {"type": "string"},
                    "runtime": {"type": "string"},
                    "stop_model_session": {"type": "boolean"},
                },
            },
        },
    }


class DeployMMSegmentationLayer(DeployMMDetectionLayer):
    action = "deploy_mmsegmentation"
    title = "Deploy MMSegmentation"


class DeployRTDETRLayer(DeployLayer):
    action = "deploy_rtdetr"
    title = "Deploy RT-DETR"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": [
                    "session_id",
                    "agent_id",
                    "device",
                    "model_source",
                    "checkpoint_name",
                    "task_type",
                    "checkpoint_url",
                    "stop_model_session",
                ],
                "properties": {
                    "session_id": {"type": "integer"},
                    "agent_id": {"type": "integer"},
                    "device": {"type": "string"},
                    "model_source": {"type": "string"},
                    "task_type": {"type": "string"},
                    "checkpoint_name": {"type": "string"},
                    "checkpoint_url": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "runtime": {"type": "string"},
                    "stop_model_session": {"type": "boolean"},
                },
            },
        },
    }


class DeployRTDETRv2Layer(DeployLayer):
    action = "deploy_rtdetrv2"
    title = "Deploy RT-DETRv2"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": [
                    "session_id",
                    "agent_id",
                    "device",
                    "model_source",
                    "model_params",
                    "stop_model_session",
                ],
                "properties": {
                    "session_id": {"type": "integer"},
                    "agent_id": {"type": "integer"},
                    "device": {"type": "string"},
                    "model_source": {"type": "string"},
                    "task_type": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "checkpoint_name": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "checkpoint_url": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "runtime": {"type": "string"},
                    "model_params": {"type": "object"},
                    "stop_model_session": {"type": "boolean"},
                },
            },
        },
    }

class DeployDEIMLayer(DeployLayer):
    action = "deploy_deim"
    title = "Deploy DEIM"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": [
                    "session_id",
                    "agent_id",
                    "device",
                    "model_source",
                    "model_params",
                    "stop_model_session",
                ],
                "properties": {
                    "session_id": {"type": "integer"},
                    "agent_id": {"type": "integer"},
                    "device": {"type": "string"},
                    "model_source": {"type": "string"},
                    "task_type": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "checkpoint_name": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "checkpoint_url": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "runtime": {"type": "string"},
                    "model_params": {"type": "object"},
                    "stop_model_session": {"type": "boolean"},
                },
            },
        },
    }

class DeployYOLOLayer(DeployLayer):
    action = "deploy_yolo"
    title = "Deploy YOLO"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": [
                    "session_id",
                    "agent_id",
                    "device",
                    "model_source",
                    "model_params",
                    "stop_model_session",
                ],
                "properties": {
                    "session_id": {"type": "integer"},
                    "agent_id": {"type": "integer"},
                    "device": {"type": "string"},
                    "model_source": {"type": "string"},
                    "task_type": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "checkpoint_name": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "checkpoint_url": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "runtime": {"type": "string"},
                    "model_params": {"type": "object"},
                    "stop_model_session": {"type": "boolean"},
                },
            },
        },
    }