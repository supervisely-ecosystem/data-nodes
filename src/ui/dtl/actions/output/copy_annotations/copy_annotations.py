from typing import Optional
from os.path import realpath, dirname

import src.globals as g

from supervisely.app.widgets import Select, Checkbox, NotificationBox

from supervisely.project.project_meta import ProjectMeta
from src.ui.dtl.utils import get_layer_docs
from src.ui.dtl import OutputAction
from src.ui.dtl.Layer import Layer

from src.ui.dtl.actions.output.copy_annotations.layout.node_widgets import (
    create_node_widgets,
)
from src.ui.dtl.actions.output.copy_annotations.layout.node_layout import (
    create_node_dst_options,
    create_node_settings_options,
)


class CopyAnnotationsAction(OutputAction):
    name = "copy_annotations"
    title = "Copy Annotations"
    docs_url = ""
    description = "Copy annotations from one project to another."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None) -> Layer:
        saved_settings = {}
        _saved_meta = None

        (
            # project selector
            # sidebar
            select_project_sidebar_dataset_selector,
            select_project_sidebar_dataset_selector_field,
            select_project_sidebar_empty_dataset_notification,
            select_project_sidebar_save_btn,
            select_project_sidebar_container,
            # preview
            select_project_preview_text,
            select_project_preview_thumbnail,
            select_project_preview_container,
            # layout
            select_project_edit_text,
            select_project_edit_btn,
            select_project_edit_container,
            # select option
            select_option,
            select_option_field,
            # backup destination
            backup_destination_project_checkbox,
            backup_destination_project_notification,
        ) = create_node_widgets()

        # SELECT PROJECT CBs
        @select_project_sidebar_save_btn.click
        def on_save_btn_click():
            _save_settings()

        # -----------------------------

        # SELECT OPTION CBs
        @select_option.value_changed
        def on_select_option_change(option):
            _save_settings()

        # -----------------------------

        # BACKUP DESTINATION CBs
        @backup_destination_project_checkbox.value_changed
        def on_backup_destination_project_checkbox_change(checked):
            if checked:
                backup_destination_project_notification.hide()
            else:
                backup_destination_project_notification.show()
            _save_settings()

        # -----------------------------

        def _update_preview():
            selected_project_id = select_project_sidebar_dataset_selector.get_selected_project_id()
            if selected_project_id is not None:
                project_info = g.api.project.get_info_by_id(selected_project_id)
                select_project_preview_thumbnail.set(project_info)
                select_project_preview_thumbnail.show()

        def get_settings(options_json: dict):
            nonlocal saved_settings
            return saved_settings

        def _set_settings_from_json(settings: dict):
            project_id = settings.get("project_id")
            if project_id is not None:
                select_project_sidebar_dataset_selector.set_project_id(project_id)
                dataset_ids = settings.get("dataset_ids")
                if dataset_ids is not None:
                    select_project_sidebar_dataset_selector.set_dataset_ids(dataset_ids)

            add_option = settings.get("add_option", "merge")
            select_option.set_value(add_option)

            backup_destination_project = settings.get("backup_destination_project", True)
            if backup_destination_project:
                backup_destination_project_checkbox.check()
                backup_destination_project_notification.hide()
            else:
                backup_destination_project_checkbox.uncheck()
                backup_destination_project_notification.show()

            _save_settings()

        def project_selected_cb(**kwargs):
            nonlocal _saved_meta
            nonlocal saved_settings
            project_meta = kwargs.get("project_meta", None)

        def _save_settings():
            nonlocal saved_settings
            nonlocal _saved_meta

            project_id = select_project_sidebar_dataset_selector.get_selected_project_id()
            dataset_ids = select_project_sidebar_dataset_selector.get_selected_ids()
            add_option = select_option.get_value()
            backup_destination_project = backup_destination_project_checkbox.is_checked()

            settings = {
                "project_id": project_id,
                "dataset_ids": dataset_ids,
                "add_option": add_option,
                "backup_destination_project": backup_destination_project,
            }
            if project_id:
                _saved_meta = g.api.project.get_meta(project_id)
                _saved_meta = ProjectMeta.from_json(_saved_meta)
                g.updater("metas")
            else:
                _saved_meta = None

            saved_settings = settings
            _update_preview()

        def get_dst(options_json: dict) -> dict:
            project_id = select_project_sidebar_dataset_selector.get_selected_project_id()
            if project_id is None:
                return []
            dst = [str(project_id)]
            return dst

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            if isinstance(dst, list):
                if len(dst) != 0:
                    project_id = int(dst[0])
                else:
                    project_id = None
            else:
                project_id = int(dst)
            select_project_sidebar_dataset_selector.set_project_id(project_id)
            _update_preview()

            dst_options = create_node_dst_options(
                select_project_edit_container,
                select_project_sidebar_container,
                select_project_preview_container,
            )
            settings_options = create_node_settings_options(
                select_option_field,
                backup_destination_project_checkbox,
                backup_destination_project_notification,
            )
            return {
                "src": [],
                "dst": dst_options,
                "settings": settings_options,
            }

        return Layer(
            action=cls,
            id=layer_id,
            create_options=create_options,
            data_changed_cb=project_selected_cb,
            get_settings=get_settings,
            get_dst=get_dst,
            need_preview=False,
        )

    @classmethod
    def create_outputs(cls):
        return []
