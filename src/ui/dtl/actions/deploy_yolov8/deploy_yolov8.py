from typing import Optional
from os.path import realpath, dirname
from supervisely import logger
from supervisely.nn.inference.session import Session
from src.ui.dtl import NeuralNetworkAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import (
    get_layer_docs,
)

from src.ui.dtl.actions.deploy_yolov8.layout.model_selector import create_model_selector_widgets
from src.ui.dtl.actions.deploy_yolov8.layout.agent_selector import create_agent_selector_widgets
from src.ui.dtl.actions.deploy_yolov8.layout.model_serve import create_model_serve_widgets
from src.ui.dtl.actions.deploy_yolov8.layout.node_layout import create_node_layout
import src.ui.dtl.actions.deploy_yolov8.layout.utils as utils
import src.globals as g


class DeployYOLOV8Action(NeuralNetworkAction):
    name = "deploy_yolov8"
    title = "Deploy YoloV8"
    docs_url = ""
    description = "Deploy YoloV8 models."
    md_description = get_layer_docs(dirname(realpath(__file__)))

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
        @agent_selector_sidebar_selector.value_changed
        def agent_selector_sidebar_selector_cb(agent_id):
            agent_selector_sidebar_device_selector.loading = True
            agent_info = g.api.agent.get_info_by_id(agent_id)
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
        ) = create_model_selector_widgets()

        # MODEL SELECTOR CBs
        @model_selector_sidebar_custom_model_option_selector.value_changed
        def model_selector_sidebar_custom_model_option_selector_cb(model_option):
            if model_option == "table":
                task_type = model_selector_sidebar_task_type_selector_custom.get_value()
                utils.check_model_avaliability_by_task_type(
                    task_type,
                    model_selector_sidebar_custom_model_table_segmentation,
                    model_selector_sidebar_custom_model_table_detection,
                    model_selector_sidebar_custom_model_table_pose_estimation,
                    model_selector_sidebar_save_btn,
                )
            else:
                model_selector_sidebar_save_btn.enable()

        @model_selector_sidebar_model_type_tabs.value_changed
        def model_selector_sidebar_model_type_tabs_cb(model_type):
            utils.check_model_avaliability_by_model_type(
                model_type,
                model_selector_sidebar_custom_model_option_selector,
                model_selector_sidebar_custom_model_table_segmentation,
                model_selector_sidebar_custom_model_table_detection,
                model_selector_sidebar_custom_model_table_pose_estimation,
                model_selector_sidebar_save_btn,
            )

        @model_selector_sidebar_task_type_selector_custom.value_changed
        def model_selector_sidebar_task_type_selector_custom_cb(task_type):
            utils.check_model_avaliability_by_task_type(
                task_type,
                model_selector_sidebar_custom_model_table_segmentation,
                model_selector_sidebar_custom_model_table_detection,
                model_selector_sidebar_custom_model_table_pose_estimation,
                model_selector_sidebar_save_btn,
            )

        @model_selector_sidebar_save_btn.click
        def model_selector_sidebar_save_btn_cb():
            nonlocal saved_settings
            saved_settings = utils.save_model_settings(
                saved_settings,
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
            utils.set_model_selector_preview(
                saved_settings, model_selector_preview, model_selector_preview_type
            )

        # -----------------------------

        (
            model_serve_preview,
            model_serve_btn,
            model_serve_layout_container,
        ) = create_model_serve_widgets()
        # RUN MODEL

        # RUN MODEL CBs
        @model_serve_btn.click
        def model_serve_btn_cb():
            nonlocal saved_settings, session
            model_serve_btn.disable()
            agent_selector_layout_edit_btn.disable()
            model_selector_layout_edit_btn.disable()

            if model_serve_btn.text == "STOP":
                utils.set_model_serve_preview("Stopping...", model_serve_preview)
                g.api.app.stop(session.task_id)
                g.running_sessions_ids.remove(session.task_id)
                model_serve_btn.text = "SERVE"
                model_serve_btn.icon = "zmdi zmdi-play"
                model_serve_btn.enable()
                agent_selector_layout_edit_btn.enable()
                model_selector_layout_edit_btn.enable()
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
                model_selector_sidebar_custom_model_option_selector,
            )
            if not success:
                agent_selector_layout_edit_btn.enable()
                model_selector_layout_edit_btn.enable()
                model_serve_btn.enable()
                return

            session = utils.start_app(g.api, g.WORKSPACE_ID, saved_settings)

            try:
                utils.set_model_serve_preview("Starting...", model_serve_preview)
                utils.deploy_model(g.api, session.task_id, saved_settings)
                logger.info(f"Session ID: {session.task_id} has been deployed")

                app_link_message = (
                    f"Model deployed - ID {session.task_id}"
                    # f"- <a href='{g.api.server_address}{g.api.app.get_url(session.task_id)}'>open app</a>"
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
        def get_data() -> dict:
            nonlocal session
            if session is not None:
                return {"session_id": session.task_id}
            else:
                return {}

        def data_changed_cb(**kwargs):
            pass

        def _save_settings() -> dict:
            nonlocal saved_settings
            saved_settings = utils.save_settings(
                saved_settings,
                agent_selector_sidebar_selector,
                agent_selector_sidebar_device_selector,
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

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return saved_settings

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
        )
