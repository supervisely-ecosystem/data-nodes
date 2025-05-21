from typing import Optional
from os.path import realpath, dirname
from supervisely import logger
from supervisely.nn.inference.session import Session
from supervisely.nn.experiments import get_experiment_infos

from src.ui.dtl.Layer import Layer

from src.ui.dtl.actions.neural_networks.deploy.layout.model_selector import (
    create_model_selector_widgets,
)
from src.ui.dtl.actions.neural_networks.deploy.layout.agent_selector import (
    create_agent_selector_widgets,
)
from src.ui.dtl.actions.neural_networks.deploy.layout.model_serve import (
    create_model_serve_widgets,
)
from src.ui.dtl.actions.neural_networks.deploy.layout.node_layout import (
    create_node_layout,
)
import src.ui.dtl.actions.neural_networks.deploy.layout.utils as utils
import src.globals as g
from src.ui.dtl.Action import DeployNNAction
from supervisely.nn.artifacts import YOLOv5v2, YOLOv8, MMDetection3, MMSegmentation, RTDETR

from src.ui.dtl.actions.neural_networks.deploy.layout.pretrained_models import (
    yolov5 as pretrained_yolov5,
    yolov8 as pretrained_yolov8,
    mmdetection3 as pretrained_mmdetection3,
    mmsegmentation as pretrained_mmsegmentation,
    rtdetr as pretrained_rtdetr,
    rtdetrv2 as pretrained_rtdetrv2,
    yolo as pretrained_yolo,
    deim as pretrained_deim,
)

class DeployBaseAction(DeployNNAction):
    name = "deploy_base"
    title = "Deploy Base"
    description = "Base layer for deployment of neural networks"
    model_params = {}
    need_runtime_selector = False

    @classmethod
    def create_inputs(self):
        return []

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        return Layer(
            action=cls,
            id=layer_id,
            need_preview=False,
            init_widgets=cls.init_widgets,
        )

    @classmethod
    def init_widgets(cls, layer: Layer):
        saved_settings = {}
        session: Session = None

        # AGENT SELECTOR
        (  # sidebar
            agent_selector_sidebar_selector,
            agent_selector_sidebar_selector_empty_message,
            agent_selector_sidebar_field,
            agent_selector_sidebar_device_selector,
            agent_selector_sidebar_device_selector_empty_message,
            agent_selector_sidebar_save_btn,
            agent_selector_sidebar_device_selector_field,
            agent_selector_sidebar_container,
            # preview
            agent_selector_preview,
            # layout
            agent_selector_layout_edit_text,
            agent_selector_layout_edit_btn,
            agent_selector_layout_container,
        ) = create_agent_selector_widgets()

        # AGENT SELECTOR CBs
        @agent_selector_layout_edit_btn.click
        def agent_selector_layout_edit_btn_cb():
            available_agents = g.api.agent.get_list_available(g.TEAM_ID, True)
            if len(available_agents) > 0:
                agent_selector_sidebar_selector.show()
                agent_selector_sidebar_selector_empty_message.hide()
            else:
                agent_selector_sidebar_selector.hide()
                agent_selector_sidebar_selector_empty_message.show()

        @agent_selector_sidebar_selector.value_changed
        def agent_selector_sidebar_selector_cb(agent_id):
            agent_selector_sidebar_device_selector.loading = True
            agents_infos = g.api.agent.get_list_available(g.TEAM_ID, True)
            for agent in agents_infos:
                if agent.id == agent_id:
                    agent_info = agent
                    break

            devices = utils.get_agent_devices(agent_info)
            agent_selector_sidebar_device_selector.set(devices)
            agent_selector_sidebar_device_selector.loading = False

        @agent_selector_sidebar_save_btn.click
        def agent_selector_sidebar_save_btn_cb():
            nonlocal saved_settings
            saved_settings = utils.save_agent_settings(
                saved_settings,
                agent_selector_sidebar_selector,
                agent_selector_sidebar_device_selector,
            )
            utils.set_agent_selector_preview(
                agent_selector_sidebar_selector,
                agent_selector_sidebar_device_selector,
                agent_selector_preview,
            )

        # -----------------------------

        # MODEL SELECTOR

        if cls.train_version == "v2":
            custom_models = get_experiment_infos(g.api, g.TEAM_ID, cls.framework_name)
        else:
            custom_models = cls.artifacts.get_list_experiment_info()
        (
            # sidebar
            # custom options
            model_selector_sidebar_custom_model_table,
            # public options
            model_selector_sidebar_public_model_table,
            model_selector_runtime_selector_sidebar,
            model_selector_runtime_field,
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
        ) = create_model_selector_widgets(
            cls.framework_name,
            cls.pretrained_models,
            custom_models,
        )
        if cls.need_runtime_selector is False:
            model_selector_runtime_field.hide()
            model_selector_runtime_selector_sidebar.set_value(None)

        # MODEL SELECTOR CBs
        @model_selector_sidebar_save_btn.click
        def model_selector_sidebar_save_btn_cb():
            nonlocal saved_settings
            saved_settings = utils.save_model_settings(
                saved_settings,
                model_selector_sidebar_model_source_tabs,
                model_selector_sidebar_public_model_table,
                model_selector_runtime_selector_sidebar,
                model_selector_sidebar_custom_model_table,
                model_selector_stop_model_after_pipeline_checkbox,
                cls.train_version,
            )
            utils.set_model_selector_preview(
                saved_settings,
                model_selector_preview,
                model_selector_preview_type,
                cls.train_version,
            )

        # -----------------------------
        (
            model_serve_preview,
            model_serve_btn,
            model_serve_layout_container,
            model_serve_postprocess_message,
        ) = create_model_serve_widgets()
        # RUN MODEL

        # RUN MODEL CBs
        @model_serve_btn.click
        def model_serve_btn_cb():
            nonlocal saved_settings, session

            model_serve_btn.disable()
            model_selector_stop_model_after_pipeline_checkbox.disable()
            agent_selector_layout_edit_btn.disable()
            model_selector_layout_edit_btn.disable()
            model_serve_postprocess_message.hide()

            if model_serve_btn.text == "STOP":
                utils.set_model_serve_preview("Stopping...", model_serve_preview)
                g.api.app.stop(session.task_id)
                g.running_sessions_ids.remove(session.task_id)
                model_serve_btn.text = "SERVE"
                model_serve_btn.icon = "zmdi zmdi-play"
                model_serve_btn.enable()
                agent_selector_layout_edit_btn.enable()
                model_selector_layout_edit_btn.enable()
                model_selector_stop_model_after_pipeline_checkbox.enable()
                utils.set_model_serve_preview(
                    "<span style='color: rgb(90, 103, 114);'>Model stopped<br>Reselect model checkpoint</span>",
                    model_serve_preview,
                )
                logger.info(f"Session ID: {session.task_id} has been stopped")
                saved_settings["session_id"] = None
                session = None
                g.updater("metas")
                return

            utils.set_model_serve_preview("", model_serve_preview)
            # add validation
            success = utils.validate_settings(
                saved_settings, model_serve_preview, cls.train_version
            )
            if not success:
                agent_selector_layout_edit_btn.enable()
                model_selector_layout_edit_btn.enable()
                model_serve_btn.enable()
                model_selector_stop_model_after_pipeline_checkbox.enable()
                return

            session = utils.start_app(
                g.api, g.WORKSPACE_ID, saved_settings, cls.framework_name, cls.slug
            )
            utils.set_model_serve_preview("Waiting for the app to start...", model_serve_preview)
            g.api.app.wait_until_ready_for_api_calls(session.task_id, 10, 10)
            try:
                utils.set_model_serve_preview("Deploying model...", model_serve_preview)
                utils.deploy_model(g.api, session.task_id, saved_settings, cls.train_version)
                logger.info(f"Session ID: {session.task_id} has been deployed")

                app_link_message = (
                    f"Model deployed - <a href='{g.api.server_address}{g.api.app.get_url(session.task_id)}' target='_blank'>open app</a>"
                    f"<br>Session ID: {session.task_id}"
                    f"<br>Press STOP to change model"
                )
                utils.set_model_serve_preview(app_link_message, model_serve_preview, "success")
                saved_settings = utils.save_model_serve_settings(saved_settings, session.task_id)
                _save_settings()
                model_serve_btn.text = "STOP"
                model_serve_btn.icon = "zmdi zmdi-pause"
                agent_selector_layout_edit_btn.disable()
                g.running_sessions_ids.append(session.task_id)
                g.updater("metas")
            except:
                utils.set_model_serve_preview(
                    "An error occured while deploying the model", model_serve_preview, "warning"
                )
                try:
                    g.api.app.stop(session.task_id)
                    g.running_sessions_ids.remove(session.task_id)
                except:
                    pass
                agent_selector_layout_edit_btn.enable()
                model_selector_layout_edit_btn.enable()
            finally:
                model_serve_btn.enable()

        # -----------------------------

        def data_changed_cb(**kwargs):
            pass

        def _save_settings() -> dict:
            nonlocal saved_settings
            saved_settings = utils.save_settings(
                saved_settings,
                agent_selector_sidebar_selector,
                agent_selector_sidebar_device_selector,
                model_selector_sidebar_model_source_tabs,
                model_selector_sidebar_public_model_table,
                model_selector_runtime_selector_sidebar,
                model_selector_sidebar_custom_model_table,
                model_selector_stop_model_after_pipeline_checkbox,
                cls.train_version,
            )

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return saved_settings

        def get_data() -> dict:
            nonlocal session
            data = {}
            if session is not None:
                data["session_id"] = session.task_id
            data["deploy_layer_name"] = layer.action.title
            data["deploy_layer_terminate"] = (
                model_selector_stop_model_after_pipeline_checkbox.is_checked()
            )
            return data

        def postprocess_cb():
            nonlocal session
            model_serve_postprocess_message.show()
            model_serve_btn.text = "SERVE"
            model_serve_btn.icon = "zmdi zmdi-play"
            model_serve_btn.enable()
            agent_selector_layout_edit_btn.enable()
            model_selector_layout_edit_btn.enable()
            model_selector_stop_model_after_pipeline_checkbox.enable()
            utils.set_model_serve_preview(
                "<span style='color: rgb(90, 103, 114);'>Model stopped<br>Reselect model checkpoint</span>",
                model_serve_preview,
            )
            saved_settings["session_id"] = None
            session = None
            g.updater("metas")

        def _set_settings_from_json(settings: dict):
            pass

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = create_node_layout(
                agent_selector_layout_container,
                agent_selector_sidebar_container,
                agent_selector_preview,
                model_selector_layout_container,
                model_selector_sidebar_container,
                model_selector_preview,
                model_selector_preview_type,
                model_selector_stop_model_after_pipeline_checkbox,
                model_serve_layout_container,
                model_serve_postprocess_message,
            )
            return {
                "src": [],
                "dst": [],
                "settings": settings_options,
            }

        layer._create_options = create_options
        layer._get_settings = get_settings
        layer._get_data = get_data
        layer.postprocess_cb = postprocess_cb


class DeployYOLOV5Action(DeployBaseAction):
    name = "deploy_yolo_v5"
    title = "Deploy YOLOv5"
    description = "Deploy YOLOv5 models."
    md_description = DeployBaseAction.read_md_file(dirname(realpath(__file__)) + "/yolov5.md")
    train_version = "v1"

    # Framework settings
    framework = "yolov5"
    framework_name = "YOLOv5"
    slug = "supervisely-ecosystem/yolov5_2.0/serve"
    artifacts = YOLOv5v2(g.TEAM_ID)
    pretrained_models = pretrained_yolov5


class DeployYOLOV8Action(DeployBaseAction):
    name = "deploy_yolo_v8"
    title = "Deploy YOLO v8 - v11"
    description = "Deploy YOLO v8 - v11 models."
    md_description = DeployBaseAction.read_md_file(dirname(realpath(__file__)) + "/yolov8.md")
    need_runtime_selector = True
    train_version = "v1"

    # Framework settings
    framework = "yolov8"
    framework_name = "YOLOv8"
    slug = "supervisely-ecosystem/yolov8/serve"
    artifacts = YOLOv8(g.TEAM_ID)
    pretrained_models = pretrained_yolov8

class DeployYOLOAction(DeployBaseAction):
    name = "deploy_yolo"
    title = "Deploy YOLO v8 - v12"
    description = "Deploy YOLO v8 - v12 models."
    md_description = DeployBaseAction.read_md_file(dirname(realpath(__file__)) + "/yolo.md")
    train_version = "v2"

    # Framework settings
    framework = "yolo"
    framework_name = "YOLO"
    slug = "supervisely-ecosystem/yolo/supervisely_integration/serve"
    artifacts = None
    pretrained_models = pretrained_yolo
    need_runtime_selector = True

class DeployMMDetectionAction(DeployBaseAction):
    name = "deploy_mmdetection"
    title = "Deploy MMDetection"
    description = "Deploy MMDetection models."
    md_description = DeployBaseAction.read_md_file(dirname(realpath(__file__)) + "/mmdetection.md")
    train_version = "v1"

    # Framework settings
    framework = "mmdetection3"
    framework_name = "MMDetection"
    slug = "supervisely-ecosystem/serve-mmdetection-v3"
    artifacts = MMDetection3(g.TEAM_ID)
    pretrained_models = pretrained_mmdetection3


class DeployMMSegmentationAction(DeployBaseAction):
    name = "deploy_mmsegmentation"
    title = "Deploy MMSegmentation"
    description = "Deploy MMSegmentation models."
    md_description = DeployBaseAction.read_md_file(
        dirname(realpath(__file__)) + "/mmsegmentation.md"
    )
    train_version = "v1"

    # Framework settings
    framework = "mmsegmentation"
    framework_name = "MMSegmentation"
    slug = "supervisely-ecosystem/mmsegmentation/serve"
    artifacts = MMSegmentation(g.TEAM_ID)
    pretrained_models = pretrained_mmsegmentation


class DeployRTDETRAction(DeployBaseAction):
    name = "deploy_rtdetr"
    title = "Deploy RT-DETR"
    description = "Deploy RT-DETR models."
    md_description = DeployBaseAction.read_md_file(dirname(realpath(__file__)) + "/rtdetr.md")
    train_version = "v1"

    # Framework settings
    framework = "rtdetr"
    framework_name = "RT-DETR"
    slug = "supervisely-ecosystem/rt-detr/supervisely_integration/serve"
    artifacts = RTDETR(g.TEAM_ID)
    pretrained_models = pretrained_rtdetr
    need_runtime_selector = True

class DeployRTDETRv2Action(DeployBaseAction):
    name = "deploy_rtdetrv2"
    title = "Deploy RT-DETRv2"
    description = "Deploy RT-DETRv2 models."
    md_description = DeployBaseAction.read_md_file(dirname(realpath(__file__)) + "/rtdetrv2.md")
    train_version = "v2"

    # Framework settings
    framework = "rtdetrv2"
    framework_name = "RT-DETRv2"
    slug = "supervisely-ecosystem/rt-detrv2/supervisely_integration/serve"
    artifacts = None
    pretrained_models = pretrained_rtdetrv2
    need_runtime_selector = True

class DeployDEIMAction(DeployBaseAction):
    name = "deploy_deim"
    title = "Deploy DEIM"
    description = "Deploy DEIM models."
    md_description = DeployBaseAction.read_md_file(dirname(realpath(__file__)) + "/deim.md")
    train_version = "v2"

    # Framework settings
    framework = "deim"
    framework_name = "DEIM"
    slug = "supervisely-ecosystem/deim/supervisely_integration/serve"
    artifacts = None
    pretrained_models = pretrained_deim
    need_runtime_selector = True

