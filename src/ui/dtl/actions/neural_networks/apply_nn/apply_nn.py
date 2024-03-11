import copy
from typing import Optional
from os.path import realpath, dirname

from supervisely import ProjectMeta
from src.ui.dtl import NeuralNetworkAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import (
    get_classes_list_value,
    get_tags_list_value,
    set_classes_list_settings_from_json,
    set_tags_list_settings_from_json,
    get_layer_docs,
)
import src.globals as g

from src.ui.dtl.actions.neural_networks.apply_nn.layout.connect_model import (
    create_connect_to_model_widgets,
)
from src.ui.dtl.actions.neural_networks.apply_nn.layout.select_classes import (
    create_classes_selector_widgets,
)
from src.ui.dtl.actions.neural_networks.apply_nn.layout.select_tags import (
    create_tags_selector_widgets,
)
from src.ui.dtl.actions.neural_networks.apply_nn.layout.inference_settings import (
    create_inference_settings_widgets,
)

from src.ui.dtl.actions.neural_networks.apply_nn.layout.node_layout import (
    create_preview_button_widget,
    create_connect_notification_widget,
    create_layout,
)

from src.ui.dtl.actions.neural_networks.apply_nn.layout.utils import *


class ApplyNNAction(NeuralNetworkAction):
    name = "apply_nn"
    title = "Apply NN"
    docs_url = ""
    description = "Connect to deployed model and apply it to images."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        _session_id = None
        _model_from_deploy_node = False
        _current_meta = ProjectMeta()
        _model_meta = ProjectMeta()
        _model_info = {}
        _model_settings = {}
        _model_connected = False

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
            always_add_suffix_checkbox,
            resolve_conflict_method_selector,
            inf_settings_editor,
            apply_nn_methods_selector,
            inf_settings_save_btn,
            inf_settings_set_default_btn,
            suffix_preview,
            use_suffix_preview,
            conflict_method_preview,
            apply_method_preview,
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
            nonlocal _current_meta, _model_meta, _model_from_deploy_node
            nonlocal _model_info, _model_settings, _model_connected, _session_id
            nonlocal saved_classes_settings, saved_tags_settings

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
                always_add_suffix_checkbox,
                resolve_conflict_method_selector,
                apply_nn_methods_selector,
                suffix_preview,
                use_suffix_preview,
                conflict_method_preview,
                apply_method_preview,
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
            g.updater("metas")
            g.updater(("nodes", layer_id))

        @connect_nn_disconnect_btn.click
        def disconnect_model():
            nonlocal _session_id
            _session_id = None
            _reset_model()

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
                apply_method_preview,
                connect_notification,
                update_preview_btn,
                model_separator,
                classes_separator,
                tags_separator,
                connect_nn_disconnect_btn,
            )

        def data_changed_cb(**kwargs):
            nonlocal _session_id, _model_from_deploy_node
            nonlocal _current_meta, _model_meta
            need_preview_update = True
            connect_nn_model_selector.enable()
            connect_nn_model_selector_disabled_text.hide()
            session_id = kwargs.get("session_id", None)
            deploy_layer_name = kwargs.get("deploy_layer_name", None)

            model_connected_text = f"Model has been connected from {deploy_layer_name} layer"
            model_disconnected_text = f"{deploy_layer_name} detected but model is not deployed"
            model_connecting_text = f"{deploy_layer_name} layer detected. Connecting to model..."
            model_waiting_text = f"Waiting for the {deploy_layer_name} to deploy model..."

            if session_id is None and deploy_layer_name is None:
                connect_nn_text.set("Connect to Model", "text")
                if _model_from_deploy_node:
                    _session_id = None
                    _reset_model()
                    _model_from_deploy_node = False
                    connect_nn_model_selector_disabled_text.hide()
                    connect_nn_model_selector.enable()
            elif session_id is None and deploy_layer_name:
                _session_id = None
                connect_nn_text.set(model_disconnected_text, "warning")
                _reset_model()
                _model_from_deploy_node = False
                connect_nn_model_selector.disable()
                connect_nn_model_selector_disabled_text.show()
            else:
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
                        need_preview_update = False
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
                        confirm_model()
                        connect_nn_text.set(model_connected_text, "success")
                    except:
                        connect_nn_text.set(model_disconnected_text, "warning")

            project_meta = kwargs.get("project_meta", None)
            if project_meta is None:
                return
            if project_meta == _current_meta:
                return
            _current_meta = project_meta
            if need_preview_update:
                g.updater(("nodes", layer_id))

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            nonlocal saved_classes_settings, saved_tags_settings
            nonlocal _model_meta, _model_info, _model_settings

            session_id = connect_nn_model_info._session_id
            apply_method = apply_nn_methods_selector.get_value()
            model_suffix = model_suffix_input.get_value()
            use_model_suffix = always_add_suffix_checkbox.is_checked()
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
                "use_model_suffix": use_model_suffix,
                "apply_method": apply_method,
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
            set_use_model_suffix_from_json(settings, always_add_suffix_checkbox)
            set_model_conflict_from_json(settings, resolve_conflict_method_selector)
            _model_settings = set_model_settings_from_json(settings, inf_settings_editor)
            set_model_apply_method_from_json(settings, apply_nn_methods_selector)
            set_model_settings_preview(
                model_suffix_input,
                always_add_suffix_checkbox,
                resolve_conflict_method_selector,
                apply_nn_methods_selector,
                suffix_preview,
                use_suffix_preview,
                conflict_method_preview,
                apply_method_preview,
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
                always_add_suffix_checkbox,
                resolve_conflict_method_selector,
                apply_nn_methods_selector,
                suffix_preview,
                use_suffix_preview,
                conflict_method_preview,
                apply_method_preview,
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
                always_add_suffix_checkbox,
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
        )
