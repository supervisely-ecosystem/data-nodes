# coding: utf-8
from typing import Tuple, Union
from time import sleep
from supervisely import (
    Annotation,
    VideoAnnotation,
    logger,
)

from supervisely.nn.inference.session import Session
from src.compute.Layer import Layer
from src.compute.dtl_utils.item_descriptor import ImageDescriptor, VideoDescriptor
import src.globals as g
from src.exceptions import BadSettingsError


def wait_model_served(session: Session, wait_attemtps: int = 10, wait_delay_sec: int = 10):
    for _ in range(wait_attemtps):
        is_model_served = session.is_model_deployed()
        if is_model_served:
            return
        else:
            sleep(wait_delay_sec)
            logger.warning("Model is not served yet. Waiting for model to be served")


def check_model_is_deployed(session_id: int):
    error_message = (
        "Selected model is not served in 'Deploy YOLOv8' node. "
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


class DeployYOLOv8Layer(Layer):
    action = "deploy_yolo_v8"

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
                    "stop_model_session": {"type": "boolean"},
                },
            },
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def validate(self):
        settings = self.settings

        if settings.get("agent_id", None) is None:
            raise BadSettingsError("Select agent in 'Deploy YOLOv8' node'")
        if settings.get("device", None) is None:
            raise BadSettingsError("Select device in 'Deploy YOLOv8' node")
        if settings.get("model_source", None) is None:
            raise BadSettingsError("Select model in 'Deploy YOLOv8' node")
        if not self.net.preview_mode:
            if settings.get("session_id", None) is None:
                raise BadSettingsError(
                    (
                        "Selected model session is not found. Make sure you have deployed model in 'Deploy YOLOv8' node. "
                        "If you still have problems, try to check model logs for more info or contact support."
                        "You can also close 'Deploy YOLOv8' node to proceed further with the workflow."
                    )
                )
            check_model_is_deployed(settings["session_id"])
            return super().validate()

    def postprocess(self):
        if self.settings["stop_model_session"]:
            session_id = self.settings["session_id"]
            g.api.app.stop(session_id)
            g.running_sessions_ids.remove(session_id)
            logger.info(f"Session ID: {session_id} has been stopped")
            self.postprocess_cb()

    def modifies_data(self):
        return False

    def process(
        self,
        data_el: Tuple[Union[ImageDescriptor, VideoDescriptor], Union[Annotation, VideoAnnotation]],
    ):
        item_desc, ann = data_el
        yield item_desc, ann
