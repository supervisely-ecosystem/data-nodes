from os.path import dirname, realpath
from typing import List, Optional

import src.globals as g
import src.utils as utils
from src.ui.dtl import SourceAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs, get_set_settings_button_style
from supervisely import ProjectMeta
from supervisely.app.widgets import Button
from supervisely.api.labeling_job_api import LabelingJobInfo

from src.ui.dtl.actions.input_labeling_job.layout.select_labeling_job import (
    create_lj_selector_widgets,
)
from src.ui.dtl.actions.input_labeling_job.layout.node_layout import create_layout
import src.ui.dtl.actions.input_labeling_job.layout.utils as utils


# ImagesProject
class InputLabelingJobAction(SourceAction):
    name = "input_labeling_job"
    title = "Input Labeling Job"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/data-layers/data"
    description = "Use to specify project and its datasets that will participate in data transformation process."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_inputs(self):
        return []

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        # Settings widgets
        _current_info = None
        _current_meta = ProjectMeta()
        saved_settings = {}
        saved_src = []

        # LJ SELECTOR
        (  # sidebar
            lj_selector_sidebar_selector,
            lj_selector_sidebar_selector_field,
            lj_selector_sidebar_lj_info,
            lj_selector_sidebar_lj_info_field,
            lj_selector_sidebar_save_btn,
            lj_selector_sidebar_container,
            # preview
            lj_selector_preview_lj_text,
            lj_selector_preview_lj_status,
            lj_selector_preview_lj_progress,
            lj_selector_preview_lj_dataset_thumbnail,
            lj_selector_preview_classes_text,
            lj_selector_preview_classes,
            lj_selector_preview_tags_text,
            lj_selector_preview_tags,
            # layout
            lj_selector_layout_text,
            lj_selector_layout_btn,
            lj_selector_layout_container,
        ) = create_lj_selector_widgets()

        # LJ SELECTOR CBs
        @lj_selector_sidebar_selector.value_changed
        def lj_selector_sidebar_selector_cb(lj_id: int):
            lj_selector_sidebar_lj_info.set_id(lj_id)

        @lj_selector_sidebar_save_btn.click
        def lj_selector_sidebar_save_btn_cb():
            nonlocal _current_meta, _current_info, saved_src, saved_settings
            job_id = lj_selector_sidebar_selector.get_value()
            job_info = g.api.labeling_job.get_info_by_id(job_id)

            project_info = g.api.project.get_info_by_id(job_info.project_id)
            dataset_info = g.api.dataset.get_info_by_id(job_info.dataset_id)
            if project_info is None or dataset_info is None:
                lj_selector_preview_lj_status.hide()
                lj_selector_preview_lj_progress.hide()
                lj_selector_preview_lj_dataset_thumbnail.hide()
                lj_selector_preview_classes.set([])
                lj_selector_preview_tags.set([])

                if project_info is None:
                    lj_selector_preview_lj_text.set(
                        f"Project: {job_info.project_name} (ID {job_info.project_id}) not found",
                        "warning",
                    )
                elif dataset_info is None:
                    lj_selector_preview_lj_text.set(
                        f"Dataset: {job_info.dataset_name} (ID {job_info.dataset_id}) not found",
                        "warning",
                    )
                update_preview_btn.disable()
                return

            job_meta = utils.get_job_meta(job_info)

            _current_meta = job_meta
            _current_info = job_info
            saved_src = [f"{job_info.project_name}/{job_info.dataset_name}"]

            utils.set_job_dataset_preview(
                project_info,
                dataset_info,
                lj_selector_preview_lj_dataset_thumbnail,
            )
            utils.set_job_classes_preview(job_meta.obj_classes, lj_selector_preview_classes)
            utils.set_job_tags_preview(job_meta.tag_metas, lj_selector_preview_tags)
            utils.set_job_name_preview(job_info.name, lj_selector_preview_lj_text)
            utils.set_job_status_preview(job_info.status, lj_selector_preview_lj_status)
            utils.set_job_progress_preview(
                job_info.accepted_images_count,
                job_info.images_count,
                lj_selector_preview_lj_progress,
            )

            _save_settings()
            g.updater("metas")
            update_preview_btn.enable()
            g.updater(("nodes", layer_id))

        # --------------------------
        # UPDATE PREVIEW BTN
        update_preview_btn = Button(
            text="Update",
            icon="zmdi zmdi-refresh",
            button_type="text",
            button_size="small",
            style=get_set_settings_button_style(),
        )
        update_preview_btn.disable()
        # -----------------------------

        def data_changed_cb(**kwargs):
            project_meta = kwargs.get("project_meta", None)
            if project_meta is None:
                return

            nonlocal _current_info, _current_meta
            if project_meta == _current_meta:
                return
            _current_meta = project_meta

        def get_src(options_json: dict) -> List[str]:
            return saved_src

        def _save_settings():
            nonlocal saved_settings, _current_info
            saved_settings = utils.save_settings(_current_info)

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return saved_settings

        def _set_src_from_json(srcs: List[str]):
            pass
            # nonlocal saved_src
            # data_changed_cb(**{"project_meta": project_meta})

        def _set_settings_from_json(settings: dict):
            utils.set_settings_from_json(
                settings,
                lj_selector_sidebar_selector,
                lj_selector_sidebar_lj_info,
                lj_selector_preview_lj_text,
                lj_selector_preview_classes,
                lj_selector_preview_tags,
            )

        def create_options(src: List[str], dst: List[str], settings: dict) -> dict:
            _set_src_from_json(src)
            _set_settings_from_json(settings)

            options = create_layout(
                lj_selector_layout_container,
                lj_selector_sidebar_container,
                lj_selector_preview_lj_text,
                lj_selector_preview_lj_status,
                lj_selector_preview_lj_progress,
                lj_selector_preview_lj_dataset_thumbnail,
                lj_selector_preview_classes_text,
                lj_selector_preview_classes,
                lj_selector_preview_tags_text,
                lj_selector_preview_tags,
            )
            return options

        return Layer(
            action=cls,
            id=layer_id,
            create_options=create_options,
            get_src=get_src,
            get_settings=get_settings,
            data_changed_cb=data_changed_cb,
            custom_update_btn=update_preview_btn,
        )
