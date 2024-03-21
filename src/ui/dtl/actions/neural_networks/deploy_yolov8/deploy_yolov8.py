from time import sleep
from typing import Optional
from os.path import realpath, dirname
from supervisely import logger
from supervisely.nn.inference.session import Session
from supervisely.api.task_api import TaskApi

from src.ui.dtl import NeuralNetworkAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import (
    get_layer_docs,
)

from src.ui.dtl.actions.neural_networks.deploy_yolov8.layout.model_selector import (
    create_model_selector_widgets,
)
from src.ui.dtl.actions.neural_networks.deploy_yolov8.layout.agent_selector import (
    create_agent_selector_widgets,
)
from src.ui.dtl.actions.neural_networks.deploy_yolov8.layout.model_serve import (
    create_model_serve_widgets,
)
from src.ui.dtl.actions.neural_networks.deploy_yolov8.layout.node_layout import (
    create_node_layout,
)
import src.ui.dtl.actions.neural_networks.deploy_yolov8.layout.utils as utils
import src.globals as g


class DeployYOLOV8Action(NeuralNetworkAction):
    name = "deploy_yolo_v8"
    title = "Deploy YOLOv8"
    docs_url = ""
    description = "Deploy YOLOv8 models."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    # @classmethod
    # def create_inputs(self):
    #     return []

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
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
        (
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
        ) = create_model_selector_widgets()

        # MODEL SELECTOR CBs
        @model_selector_sidebar_save_btn.click
        def model_selector_sidebar_save_btn_cb():
            nonlocal saved_settings
            saved_settings = utils.save_model_settings(
                saved_settings,
                model_selector_sidebar_model_source_tabs,
                model_selector_sidebar_public_model_table,
                model_selector_sidebar_custom_model_table,
                model_selector_stop_model_after_pipeline_checkbox,
            )
            utils.set_model_selector_preview(
                saved_settings, model_selector_preview, model_selector_preview_type
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
                saved_settings,
                model_serve_preview,
            )
            if not success:
                agent_selector_layout_edit_btn.enable()
                model_selector_layout_edit_btn.enable()
                model_serve_btn.enable()
                model_selector_stop_model_after_pipeline_checkbox.enable()
                return

            session = utils.start_app(g.api, g.WORKSPACE_ID, saved_settings)
            utils.set_model_serve_preview("Waiting for the app to start...", model_serve_preview)
            g.api.app.wait_until_ready_for_api_calls(session.task_id, 10, 10)
            try:
                utils.set_model_serve_preview("Deploying model...", model_serve_preview)
                utils.deploy_model(g.api, session.task_id, saved_settings)
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
                model_selector_sidebar_custom_model_table,
                model_selector_stop_model_after_pipeline_checkbox,
            )

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return saved_settings

        def get_data() -> dict:
            nonlocal session
            data = {}
            if session is not None:
                data["session_id"] = session.task_id
            data["deploy_layer_name"] = "Deploy YOLOv8"
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

        return Layer(
            action=cls,
            id=layer_id,
            create_options=create_options,
            get_settings=get_settings,
            get_data=get_data,
            need_preview=False,
            postprocess_cb=postprocess_cb,
        )
