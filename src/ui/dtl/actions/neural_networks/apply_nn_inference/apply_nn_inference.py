import copy
from os.path import dirname, realpath
from typing import Optional

from supervisely import ProjectMeta
from supervisely.app.widgets import NodesFlow

import src.globals as g
from src.ui.dtl.Action import ApplyNNAction
from src.ui.dtl.actions.neural_networks.apply_nn_inference.layout.connect_model import (
    create_connect_to_model_widgets,
)
from src.ui.dtl.actions.neural_networks.apply_nn_inference.layout.inference_settings import (
    create_inference_settings_widgets,
)
from src.ui.dtl.actions.neural_networks.apply_nn_inference.layout.node_layout import (
    create_connect_notification_widget,
    create_layout,
    create_preview_button_widget,
)
from src.ui.dtl.actions.neural_networks.apply_nn_inference.layout.select_classes import (
    create_classes_selector_widgets,
)
from src.ui.dtl.actions.neural_networks.apply_nn_inference.layout.select_tags import (
    create_tags_selector_widgets,
)
from src.ui.dtl.actions.neural_networks.apply_nn_inference.layout.utils import *
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import (
    get_classes_list_value,
    get_layer_docs,
    get_tags_list_value,
    set_classes_list_settings_from_json,
    set_tags_list_settings_from_json,
)


class ApplyNNInferenceAction(ApplyNNAction):
    name = "apply_nn_inference"
    legacy_name = "apply_nn"
    title = "Apply NN Inference"
    docs_url = ""
    description = "Connect to deployed model and apply it to images."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_inputs(cls):
        return [
            NodesFlow.Node.Input("deployed_model", "Deployed model (optional)", color="#000000"),
            NodesFlow.Node.Input("source", "Input", color="#000000"),
        ]

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        _session_id = None
        _model_from_deploy_node = False
        _current_meta = ProjectMeta()
        _model_meta = ProjectMeta()
        _model_info = {}
        _model_settings = {}
        _model_connected = False
        _kill_deployed_model_after_pipeline = False
        _deploy_layer_name = ""
        _need_preview_update = True
        _prev_connections = []
        _deploy_node_is_connected = False
        _model_from_apply_node = False  # when connect button is pressed

        (
            connect_nn_text,
            connect_nn_model_preview,
            connect_nn_edit_btn,
            connect_nn_edit_container,
            connect_nn_connect_btn,
            connect_nn_disconnect_btn,
            connect_nn_model_selector,
            connect_nn_model_field,
            connect_nn_model_selector_disabled_text,
            connect_nn_model_info,
            connect_nn_model_info_empty_text,
            connect_nn_model_info_container,
            connect_nn_model_info_field,
            connect_nn_widgets_container,
            model_separator,
        ) = create_connect_to_model_widgets()

        (
            model_suffix_input,
            add_suffix_method_selector,
            add_suffix_method_field,
            ignore_labeled_checkbox,
            resolve_conflict_method_selector,
            inf_settings_editor,
            apply_nn_methods_selector,
            batch_size_input,
            inf_settings_save_btn,
            inf_settings_set_default_btn,
            suffix_preview,
            use_suffix_preview,
            conflict_method_preview,
            ignore_labeled_preview,
            apply_method_preview,
            batch_size_preview,
            inf_settings_edit_text,
            inf_settings_edit_container,
            inf_settings_widgets_container,
            inf_settings_preview_container,
        ) = create_inference_settings_widgets()

        (
            classes_list_widget_notification,
            classes_list_widget,
            classes_list_preview,
            classes_list_save_btn,
            classes_list_set_default_btn,
            classes_list_widget_field,
            classes_list_widgets_container,
            classes_list_edit_text,
            classes_list_edit_btn,
            classes_list_edit_container,
            classes_separator,
        ) = create_classes_selector_widgets()

        (
            tags_list_widget_notification,
            tags_list_widget,
            tags_list_preview,
            tags_list_save_btn,
            tags_list_set_default_btn,
            tags_list_widget_field,
            tags_list_widgets_container,
            tags_list_edit_text,
            tags_list_edit_btn,
            tags_list_edit_container,
            tags_separator,
        ) = create_tags_selector_widgets()

        connect_notification = create_connect_notification_widget()
        update_preview_btn = create_preview_button_widget()

        ### CONNECT TO MODEL BUTTONS
        @connect_nn_model_selector.value_changed
        def select_model_session(session_id):
            if session_id is None:
                return
            update_model_info_preview(
                session_id,
                connect_nn_model_info_empty_text,
                connect_nn_model_info,
                connect_nn_connect_btn,
            )

        @connect_nn_connect_btn.click
        def confirm_model():
            nonlocal _current_meta, _model_meta, _model_from_deploy_node, _need_preview_update
            nonlocal _model_info, _model_settings, _model_connected, _session_id
            nonlocal saved_classes_settings, saved_tags_settings, _model_from_apply_node

            _model_from_apply_node = False
            connect_nn_model_selector.disable()
            connect_nn_connect_btn.disable()
            connect_nn_disconnect_btn.disable()

            classes_separator.hide()
            tags_separator.hide()
            model_separator.hide()

            connect_notification.loading = True
            update_preview_btn.disable()

            _session_id = connect_nn_model_info._session_id
            if _session_id is None:
                connect_notification.loading = False
                connect_nn_model_selector.enable()
                _model_connected = False
                return

            model_meta, model_info, model_settings = get_model_settings(
                _session_id,
                connect_notification,
                connect_nn_model_selector,
                connect_nn_model_info,
                connect_nn_model_info_empty_text,
                _model_from_deploy_node,
            )
            if model_meta is None and model_info is None and model_settings is None:
                connect_notification.loading = False
                connect_nn_model_selector.enable()
                _model_connected = False
                return
            else:
                _model_meta = model_meta
                _model_info = model_info
                _model_settings = model_settings

            set_model_preview(_model_info, connect_nn_model_preview)
            set_model_settings(_model_settings, inf_settings_editor)
            connect_nn_model_preview.show()

            classes_separator.show()
            classes_list_edit_text.show()
            saved_classes_settings = set_model_classes(
                classes_list_widget, [obj_class for obj_class in _model_meta.obj_classes]
            )
            set_model_classes_preview(
                classes_list_widget,
                classes_list_preview,
                saved_classes_settings,
                classes_list_edit_text,
                "Model Classes",
            )

            tags_separator.show()
            tags_list_edit_text.show()
            saved_tags_settings = set_model_tags(
                tags_list_widget, [tag_meta for tag_meta in _model_meta.tag_metas]
            )
            set_model_tags_preview(
                tags_list_widget, tags_list_preview, saved_tags_settings, tags_list_edit_text
            )

            connect_notification.hide()
            connect_notification.loading = False

            model_separator.show()
            inf_settings_edit_text.show()
            set_model_settings_preview(
                model_suffix_input,
                add_suffix_method_selector,
                ignore_labeled_checkbox,
                resolve_conflict_method_selector,
                apply_nn_methods_selector,
                batch_size_input,
                suffix_preview,
                use_suffix_preview,
                conflict_method_preview,
                ignore_labeled_preview,
                apply_method_preview,
                batch_size_preview,
            )

            show_node_gui(
                connect_nn_model_preview,
                classes_list_edit_container,
                classes_list_preview,
                tags_list_edit_container,
                tags_list_preview,
                inf_settings_edit_container,
            )
            update_preview_btn.enable()
            connect_nn_model_selector.disable()
            connect_nn_connect_btn.disable()
            connect_nn_disconnect_btn.enable()
            _model_connected = True
            _model_from_apply_node = True
            g.updater("metas")
            if _need_preview_update:
                g.updater(("nodes", layer_id))

        @connect_nn_disconnect_btn.click
        def disconnect_model():
            nonlocal _session_id
            _session_id = None
            _reset_model()
            g.updater(("nodes", layer_id))

        ### -----------------------

        saved_classes_settings = "default"
        default_classes_settings = "default"

        saved_tags_settings = "default"
        default_tags_settings = "default"

        def _get_classes_list_value():
            return get_classes_list_value(classes_list_widget, multiple=True)

        def _get_tags_list_value():
            return get_tags_list_value(tags_list_widget, multiple=True)

        def _save_classes_list_settings():
            nonlocal saved_classes_settings
            saved_classes_settings = _get_classes_list_value()

        def _save_tags_list_settings():
            nonlocal saved_tags_settings
            saved_tags_settings = _get_tags_list_value()

        def _set_default_classes_list_setting():
            # save setting to var
            nonlocal saved_classes_settings
            saved_classes_settings = copy.deepcopy(default_classes_settings)

        def _set_default_tags_list_setting():
            # save setting to var
            nonlocal saved_tags_settings
            saved_tags_settings = copy.deepcopy(default_tags_settings)

        def _reset_model():
            reset_model(
                connect_nn_model_selector,
                connect_nn_model_info,
                connect_nn_model_info_empty_text,
                connect_nn_model_preview,
                classes_list_widget,
                classes_list_preview,
                classes_list_edit_container,
                tags_list_widget,
                tags_list_preview,
                tags_list_edit_container,
                inf_settings_edit_container,
                suffix_preview,
                use_suffix_preview,
                conflict_method_preview,
                ignore_labeled_preview,
                apply_method_preview,
                batch_size_preview,
                connect_notification,
                update_preview_btn,
                model_separator,
                classes_separator,
                tags_separator,
                connect_nn_disconnect_btn,
            )

        def meta_change_cb(project_meta: ProjectMeta):
            nonlocal _current_meta
            if project_meta is None:
                return
            if project_meta == _current_meta:
                return
            _current_meta = project_meta

        def data_changed_cb(**kwargs):
            nonlocal _deploy_node_is_connected, _model_from_apply_node
            nonlocal _session_id, _model_from_deploy_node, _deploy_layer_name
            nonlocal _need_preview_update, _kill_deployed_model_after_pipeline
            if _session_id == "reset":
                session_id = None
            else:
                session_id = kwargs.get("session_id", None)

            _deploy_layer_name = kwargs.get("deploy_layer_name", None)
            _kill_deployed_model_after_pipeline = kwargs.get("deploy_layer_terminate", False)

            model_connected_text = f"Model has been connected from {_deploy_layer_name} layer"
            model_disconnected_text = f"{_deploy_layer_name} detected but model is not deployed"
            model_connecting_text = f"{_deploy_layer_name} layer detected. Connecting to model..."
            model_waiting_text = f"Waiting for the {_deploy_layer_name} to deploy model..."
            if (
                session_id is None
                and _model_from_apply_node is False
                and _deploy_layer_name is None
                and _deploy_node_is_connected is False
            ):
                if connect_nn_text.text == "Connected layer is not a deploy model layer":
                    pass
                elif (
                    connect_nn_text.text == "Multiple connections to deployed model are not allowed"
                ):
                    pass
                else:
                    connect_nn_text.set("Connect to Model", "text")
                _session_id = None
                _reset_model()
                _model_from_deploy_node = False
                connect_nn_model_selector_disabled_text.hide()
                connect_nn_model_selector.enable()
            elif session_id is None and _deploy_layer_name and _deploy_node_is_connected:
                _session_id = None
                connect_nn_text.set(model_disconnected_text, "warning")
                _reset_model()
                _model_from_apply_node = False
                _model_from_deploy_node = False
                connect_nn_model_selector.disable()
                connect_nn_model_selector_disabled_text.show()
            elif session_id and _deploy_layer_name and _deploy_node_is_connected:
                _model_from_apply_node = False
                _model_from_deploy_node = True
                connect_nn_model_selector.disable()
                connect_nn_model_selector_disabled_text.show()
                connect_nn_disconnect_btn.disable()

                if connect_nn_text.text != model_connected_text:
                    connect_nn_text.set(model_connecting_text, "text")

                if session_id == _session_id:
                    connect_nn_text.set(model_connected_text, "success")
                    return
                else:
                    _session_id = session_id

                    try:
                        is_ready = g.api.app.is_ready_for_api_calls(_session_id)
                        if not is_ready:
                            connect_nn_text.set(model_waiting_text, "text")
                            g.api.app.wait_until_ready_for_api_calls(_session_id)

                        session = Session(g.api, _session_id)
                        connect_nn_text.set(model_connecting_text, "text")
                        connect_nn_model_selector.set_session_id(_session_id)
                        update_model_info_preview(
                            _session_id,
                            connect_nn_model_info_empty_text,
                            connect_nn_model_info,
                            connect_nn_connect_btn,
                        )
                        _need_preview_update = False
                        confirm_model()
                        _model_from_apply_node = False
                        _need_preview_update = True
                        connect_nn_text.set(model_connected_text, "success")
                    except:
                        connect_nn_text.set(model_disconnected_text, "warning")

            elif (
                _session_id is not None
                and _session_id != "reset"
                and _model_from_apply_node is True
                and _deploy_layer_name is None
                and _deploy_node_is_connected is False
            ):
                # model set from apply nn layer
                # _session_id = session_id
                print("model set from apply nn layer")
                pass

            if "project_meta" in kwargs:
                project_meta = kwargs.get("project_meta", None)
                meta_change_cb(project_meta)

        def update_sources_cb(connections: List[tuple]) -> List[bool]:
            nonlocal _prev_connections, _deploy_node_is_connected

            need_append = [True] * len(connections)
            if connections == _prev_connections:
                return need_append

            _deploy_node_is_connected = False
            _prev_connections = connections
            deployed_model_connections = []
            for idx, (src_name, to_node_interface) in enumerate(connections):
                if to_node_interface == "deployed_model":
                    deployed_model_connections.append(src_name)
                    need_append[idx] = False

            if len(deployed_model_connections) > 1:
                connect_nn_text.set(
                    "Multiple connections to deployed model are not allowed",
                    "warning",
                )
                _deploy_node_is_connected = False
                return need_append

            elif len(deployed_model_connections) == 1:
                src_name = deployed_model_connections[0]
                if src_name.startswith("$deploy_"):
                    _deploy_node_is_connected = True
                else:
                    _deploy_node_is_connected = False
                    connect_nn_text.set(
                        "Connected layer is not a deploy model layer",
                        "warning",
                    )
            else:
                _deploy_node_is_connected = False
                connect_nn_text.set("Connect to Model", "text")
            return need_append

        def postprocess_cb():  # causes file not found error
            nonlocal _session_id, _kill_deployed_model_after_pipeline
            if _kill_deployed_model_after_pipeline:
                _session_id = "reset"
                _reset_model()

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            nonlocal saved_classes_settings, saved_tags_settings
            nonlocal _model_meta, _model_info, _model_settings

            session_id = connect_nn_model_info._session_id
            apply_method = apply_nn_methods_selector.get_value()
            batch_size = batch_size_input.get_value()
            model_suffix = model_suffix_input.get_value()

            add_suffix_method = add_suffix_method_selector.get_value()
            ignore_labeled = ignore_labeled_checkbox.is_checked()
            add_pred_ann_method = resolve_conflict_method_selector.get_value()
            model_settings_json = model_settings_from_yaml(_model_settings, inf_settings_editor)

            settings = {
                "current_meta": _current_meta.to_json(),
                "session_id": session_id,
                "model_info": _model_info,
                "model_meta": _model_meta.to_json(),
                "model_settings": model_settings_json,
                "model_suffix": model_suffix,
                "add_pred_ann_method": add_pred_ann_method,
                "add_suffix_method": add_suffix_method,
                "ignore_labeled": ignore_labeled,
                "apply_method": apply_method,
                "batch_size": batch_size,
                "classes": saved_classes_settings,
                "tags": saved_tags_settings,
            }
            return settings

        def _set_settings_from_json(settings: dict):
            nonlocal _model_meta, _model_info, _model_settings, _session_id
            connect_notification.loading = True
            _session_id = set_deployed_model_from_json(settings, connect_nn_model_selector)
            if _session_id is None:
                connect_notification.loading = False
                return

            connect_notification.hide()
            connect_notification.loading = False
            show_node_gui(
                connect_nn_model_preview,
                classes_list_edit_container,
                classes_list_preview,
                tags_list_edit_container,
                tags_list_preview,
                inf_settings_edit_container,
            )

            # model
            _model_info = set_model_info_from_json(
                settings,
                connect_nn_model_info_empty_text,
                connect_nn_model_info,
                connect_nn_connect_btn,
            )
            set_model_preview(_model_info, connect_nn_model_preview)
            _model_meta = set_model_meta_from_json(settings)
            # -----------------------

            # classes
            classes_list_widget.loading = True
            classes_list_settings = settings.get("classes", [])
            classes_list_widget.set(_model_meta.obj_classes)
            set_classes_list_settings_from_json(classes_list_widget, classes_list_settings)
            _save_classes_list_settings()
            set_classes_list_preview(
                classes_list_widget,
                classes_list_preview,
                classes_list_settings,
                classes_list_edit_text,
                "Model Classes",
            )
            classes_list_widget.loading = False
            # -----------------------

            # tags
            tags_list_widget.loading = True
            tags_list_settings = settings.get("tags", [])
            tags_list_widget.set(_model_meta.tag_metas)
            set_tags_list_settings_from_json(tags_list_widget, tags_list_settings)
            _save_tags_list_settings()
            set_tags_list_preview(
                tags_list_widget,
                tags_list_preview,
                tags_list_settings,
                tags_list_edit_text,
                "Model Tags",
            )
            tags_list_widget.loading = False
            # -----------------------

            # model settings
            set_model_suffix_from_json(settings, model_suffix_input)
            set_use_model_suffix_from_json(settings, add_suffix_method_selector)
            set_model_conflict_from_json(settings, resolve_conflict_method_selector)
            _model_settings = set_model_settings_from_json(settings, inf_settings_editor)
            set_model_apply_method_from_json(settings, apply_nn_methods_selector)
            set_batch_size_from_json(settings, batch_size_input)
            set_model_settings_preview(
                model_suffix_input,
                add_suffix_method_selector,
                ignore_labeled_checkbox,
                resolve_conflict_method_selector,
                apply_nn_methods_selector,
                batch_size_input,
                suffix_preview,
                use_suffix_preview,
                conflict_method_preview,
                ignore_labeled_preview,
                apply_method_preview,
                batch_size_preview,
            )
            # -----------------------
            update_preview_btn.enable()

        @classes_list_save_btn.click
        def classes_list_save_btn_cb():
            _save_classes_list_settings()
            set_model_classes_preview(
                classes_list_widget,
                classes_list_preview,
                saved_classes_settings,
                classes_list_edit_text,
                "Model Classes",
            )
            g.updater("metas")

        @classes_list_set_default_btn.click
        def classes_list_set_default_btn_cb():
            _set_default_classes_list_setting()
            set_classes_list_settings_from_json(classes_list_widget, saved_classes_settings)
            set_model_classes_preview(
                classes_list_widget,
                classes_list_preview,
                saved_classes_settings,
                classes_list_edit_text,
                "Model Classes",
            )
            g.updater("metas")

        @tags_list_save_btn.click
        def tags_list_save_btn_cb():
            _save_tags_list_settings()
            set_tags_list_preview(
                tags_list_widget,
                tags_list_preview,
                saved_tags_settings,
                tags_list_edit_text,
                "Model Tags",
            )
            g.updater("metas")

        @tags_list_set_default_btn.click
        def tags_list_set_default_btn_cb():
            _set_default_tags_list_setting()
            set_tags_list_settings_from_json(tags_list_widget, saved_tags_settings)
            set_tags_list_preview(
                tags_list_widget,
                tags_list_preview,
                saved_tags_settings,
                tags_list_edit_text,
                "Model Tags",
            )
            g.updater("metas")

        @inf_settings_save_btn.click
        def inf_settings_save_btn_cb():
            nonlocal _session_id, _model_settings
            update_model_inference_settings(_session_id, _model_settings, inf_settings_editor)
            set_model_settings_preview(
                model_suffix_input,
                add_suffix_method_selector,
                ignore_labeled_checkbox,
                resolve_conflict_method_selector,
                apply_nn_methods_selector,
                batch_size_input,
                suffix_preview,
                use_suffix_preview,
                conflict_method_preview,
                ignore_labeled_preview,
                apply_method_preview,
                batch_size_preview,
            )
            g.updater("metas")

        @inf_settings_set_default_btn.click
        def inf_settings_set_default_btn_cb():
            nonlocal _session_id
            if _session_id is None:
                return

            set_default_model_settings(
                _session_id,
                model_suffix_input,
                add_suffix_method_selector,
                resolve_conflict_method_selector,
                apply_nn_methods_selector,
                inf_settings_editor,
                connect_nn_model_preview,
            )
            g.updater("metas")

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = create_layout(
                connect_nn_edit_container,
                connect_nn_widgets_container,
                connect_nn_model_preview,
                connect_notification,
                classes_list_edit_container,
                classes_list_widgets_container,
                classes_list_preview,
                tags_list_edit_container,
                tags_list_widgets_container,
                tags_list_preview,
                inf_settings_edit_container,
                inf_settings_widgets_container,
                inf_settings_preview_container,
                model_separator,
                classes_separator,
                tags_separator,
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
            data_changed_cb=data_changed_cb,
            custom_update_btn=update_preview_btn,
            postprocess_cb=postprocess_cb,
            update_sources_cb=update_sources_cb,
        )
