import copy
from typing import Optional
from os.path import realpath, dirname

from supervisely import ProjectMeta

from src.ui.dtl import OutputAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import (
    get_layer_docs,
    classes_list_settings_changed_meta,
    set_classes_list_settings_from_json,
    set_classes_list_preview,
    get_classes_list_value,
    tags_list_settings_changed_meta,
    set_tags_list_settings_from_json,
    set_tags_list_preview,
    get_tags_list_value,
    set_members_list_settings_from_json,
    set_members_list_preview,
    get_members_list_value,
)

from src.ui.dtl.actions.output.create_labeling_job.layout.job_description import (
    create_job_description_widgets,
)
from src.ui.dtl.actions.output.create_labeling_job.layout.job_members import (
    create_job_members_widgets,
)
from src.ui.dtl.actions.output.create_labeling_job.layout.job_settings_classes import (
    create_job_settings_classes_widgets,
)
from src.ui.dtl.actions.output.create_labeling_job.layout.job_settings_tags import (
    create_job_settings_tags_widgets,
)
from src.ui.dtl.actions.output.create_labeling_job.layout.node_layout import create_settings_options
from src.ui.dtl.actions.output.create_labeling_job.layout.job_output import (
    create_job_output_widgets,
)
import src.ui.dtl.actions.output.create_labeling_job.layout.utils as lj_utils
import src.globals as g


class CreateLabelingJobAction(OutputAction):
    name = "create_labeling_job"
    legacy_name = "labeling_job"
    title = "Create Labeling Job"
    docs_url = ""
    description = "Creates Labeling Job with given parameters."
    md_description = get_layer_docs(dirname(realpath(__file__)))
    width = 360

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        _current_meta = ProjectMeta()
        saved_settings = {}
        modifies_data = False

        saved_classes_settings = "default"
        default_classes_settings = "default"

        saved_tags_settings = "default"
        default_tags_settings = "default"

        saved_members_settings = []
        default_members_settings = []

        # DESCRIPTION
        (
            # sidebar
            lj_description_title_input,
            lj_description_description_editor,
            lj_description_readme_editor,
            lj_description_save_btn,
            lj_description_sidebar_container,
            # preview
            lj_description_title_preview,
            # layout
            lj_description_container,
        ) = create_job_description_widgets()

        # DESCRIPTION CBs
        @lj_description_save_btn.click
        def description_save_btn_cb():
            lj_utils.set_lj_name_preview(lj_description_title_input, lj_description_title_preview)
            _save_settings()

        # ----------------------------

        # MEMBERS
        (
            # sidebar
            lj_members_reviewer_selector,
            lj_members_labelers_list,
            lj_members_save_btn,
            lj_members_sidebar_container,
            # preview
            lj_members_reviewer_preview,
            lj_members_labelers_list_preview,
            lj_members_preview_container,
            # layout
            lj_members_container,
        ) = create_job_members_widgets()

        # MEMBERS CBs
        @lj_members_save_btn.click
        def members_save_btn_cb():
            lj_utils.set_lj_reviewer_preview(
                lj_members_reviewer_selector, lj_members_reviewer_preview
            )
            _save_members_list_settings()
            set_members_list_preview(
                lj_members_labelers_list,
                lj_members_labelers_list_preview,
                saved_members_settings,
            )
            _save_settings()
            return

        # ----------------------------

        # CLASSES
        (
            # sidebar
            lj_settings_classes_list_widget,
            lj_settings_classes_list_save_btn,
            lj_settings_classes_list_set_default_btn,
            lj_settings_classes_list_widgets_container,
            # preview
            lj_settings_classes_list_preview,
            # layout
            lj_settings_classes_list_edit_text,
            lj_settings_classes_list_edit_btn,
            lj_settings_classes_list_edit_container,
        ) = create_job_settings_classes_widgets()

        # CLASSES CBs
        @lj_settings_classes_list_save_btn.click
        def classes_save_btn_cb():
            _save_classes_list_settings()
            set_classes_list_preview(
                lj_settings_classes_list_widget,
                lj_settings_classes_list_preview,
                saved_classes_settings,
                lj_settings_classes_list_edit_text,
            )
            _save_settings()
            g.updater("metas")

        @lj_settings_classes_list_set_default_btn.click
        def classes_set_default_btn_cb():
            _set_default_classes_list_setting()
            set_classes_list_settings_from_json(
                lj_settings_classes_list_widget, saved_classes_settings
            )
            # set_classes_list_preview(
            #     lj_settings_classes_list_widget,
            #     lj_settings_classes_list_preview,
            #     saved_classes_settings,
            # )
            _save_settings()
            g.updater("metas")

        # ----------------------------

        # TAGS
        (
            # sidebar
            lj_settings_tags_list_widget,
            lj_settings_tags_list_save_btn,
            lj_settings_tags_list_set_default_btn,
            lj_settings_tags_list_widgets_container,
            # preview
            lj_settings_tags_list_preview,
            # layout
            lj_settings_tags_list_edit_text,
            lj_settings_tags_list_edit_btn,
            lj_settings_tags_list_edit_container,
        ) = create_job_settings_tags_widgets()

        # TAGS CBs
        @lj_settings_tags_list_save_btn.click
        def tags_save_btn_cb():
            _save_tags_list_settings()
            set_tags_list_preview(
                lj_settings_tags_list_widget,
                lj_settings_tags_list_preview,
                saved_tags_settings,
                lj_settings_tags_list_edit_text,
            )
            _save_settings()
            g.updater("metas")

        @lj_settings_tags_list_set_default_btn.click
        def tags_set_default_btn_cb():
            _set_default_tags_list_setting()
            set_tags_list_settings_from_json(lj_settings_tags_list_widget, saved_tags_settings)
            # set_tags_list_preview(
            #     lj_settings_tags_list_widget, lj_settings_tags_list_preview, saved_tags_settings
            # )
            _save_settings()
            g.updater("metas")

        # ----------------------------

        # OUTPUT
        (
            # sidebar
            lj_output_project_name_input,
            lj_output_dataset_keep_checkbox,
            lj_output_dataset_name_input,
            lj_output_save_btn,
            lj_output_sidebar_container,
            # preview
            lj_output_project_name_preview,
            lj_output_dataset_name_preview,
            lj_output_container_preview,
            lj_output_modifies_data_preview,
            # layout
            lj_output_edit_btn,
            lj_output_edit_container,
        ) = create_job_output_widgets()

        # OUTPUT CBs
        @lj_output_edit_btn.click
        def output_edit_btn_cb():
            nonlocal modifies_data
            lj_utils.set_output_preview(
                modifies_data,
                lj_output_edit_btn,
                lj_output_modifies_data_preview,
                lj_output_project_name_preview,
                lj_output_dataset_name_preview,
            )
            # hide whole container? lj_output_edit_container.hide()

        @lj_output_save_btn.click
        def dataset_save_btn_cb():
            lj_utils.set_lj_output_project_name_preview(
                lj_output_project_name_input, lj_output_project_name_preview
            )
            lj_utils.set_lj_output_dataset_name_preview(
                lj_output_dataset_name_input,
                lj_output_dataset_keep_checkbox,
                lj_output_dataset_name_preview,
            )
            _save_settings()
            return

        @lj_output_dataset_keep_checkbox.value_changed
        def dataset_keep_checkbox_cb(is_checked):
            if is_checked:
                lj_output_dataset_name_input.hide()
            else:
                lj_output_dataset_name_input.show()

        # ----------------------------

        def _set_default_classes_list_setting():
            nonlocal saved_classes_settings
            saved_classes_settings = copy.deepcopy(default_classes_settings)

        def _set_default_tags_list_setting():
            nonlocal saved_tags_settings
            saved_tags_settings = copy.deepcopy(default_tags_settings)

        def _set_default_members_list_setting():
            nonlocal saved_members_settings
            saved_members_settings = copy.deepcopy(default_members_settings)

        def _get_classes_list_value():
            return get_classes_list_value(lj_settings_classes_list_widget, multiple=True)

        def _get_tags_list_value():
            return get_tags_list_value(lj_settings_tags_list_widget, multiple=True)

        def _get_members_list_value():
            return get_members_list_value(lj_members_labelers_list, multiple=True)

        def _save_classes_list_settings():
            nonlocal saved_classes_settings
            saved_classes_settings = _get_classes_list_value()

        def _save_tags_list_settings():
            nonlocal saved_tags_settings
            saved_tags_settings = _get_tags_list_value()

        def _save_members_list_settings():
            nonlocal saved_members_settings
            saved_members_settings = _get_members_list_value()

        def _set_classes_list_preview():
            set_classes_list_preview(
                lj_settings_classes_list_widget,
                lj_settings_classes_list_preview,
                saved_classes_settings,
            )

        def _set_tags_list_preview():
            set_tags_list_preview(
                lj_settings_tags_list_widget,
                lj_settings_tags_list_preview,
                saved_tags_settings,
            )

        def _set_members_list_preview():
            set_members_list_preview(
                lj_members_labelers_list,
                lj_members_labelers_list_preview,
                saved_members_settings,
            )

        def meta_change_cb(project_meta):
            nonlocal _current_meta
            if project_meta == _current_meta:
                return

            _current_meta = project_meta

            lj_settings_classes_list_widget.loading = True
            lj_settings_tags_list_widget.loading = True
            lj_members_labelers_list.loading = True

            obj_classes = project_meta.obj_classes
            lj_settings_classes_list_widget.set(obj_classes)
            lj_settings_classes_list_edit_text.set(f"Classes: 0 / {len(obj_classes)}", "text")

            tag_metas = project_meta.tag_metas
            lj_settings_tags_list_widget.set(tag_metas)
            lj_settings_tags_list_edit_text.set(f"Tags: 0 / {len(tag_metas)}", "text")

            nonlocal saved_classes_settings
            saved_classes_settings = classes_list_settings_changed_meta(
                saved_classes_settings,
                obj_classes,
            )
            nonlocal saved_tags_settings
            saved_tags_settings = tags_list_settings_changed_meta(
                saved_tags_settings,
                tag_metas,
            )

            set_classes_list_settings_from_json(
                lj_settings_classes_list_widget,
                saved_classes_settings,
            )
            set_tags_list_settings_from_json(
                lj_settings_tags_list_widget,
                saved_tags_settings,
            )
            set_members_list_settings_from_json(
                lj_members_labelers_list,
                saved_members_settings,
            )

            _set_classes_list_preview()
            _set_tags_list_preview()
            _set_members_list_preview()

            lj_settings_classes_list_widget.loading = False
            lj_settings_tags_list_widget.loading = False
            lj_members_labelers_list.loading = False

        def data_changed_cb(**kwargs):
            if "modifies_data" in kwargs:
                nonlocal modifies_data
                modifies_data = kwargs.get("modifies_data", False)
                lj_utils.set_output_preview(
                    modifies_data,
                    lj_output_edit_btn,
                    lj_output_modifies_data_preview,
                    lj_output_project_name_preview,
                    lj_output_dataset_name_preview,
                )

            if "project_meta" in kwargs:
                project_meta = kwargs.get("project_meta", ProjectMeta())
                meta_change_cb(project_meta)

            _save_settings()
            g.updater("metas")

        def _save_settings():
            nonlocal saved_settings, saved_classes_settings, saved_tags_settings
            settings = lj_utils.save_settings(
                lj_description_title_input,
                lj_description_readme_editor,
                lj_description_description_editor,
                lj_members_reviewer_selector,
                lj_members_labelers_list,
                saved_classes_settings,
                saved_tags_settings,
                lj_output_project_name_input,
                lj_output_dataset_keep_checkbox,
                lj_output_dataset_name_input,
                modifies_data,
            )
            saved_settings = settings

        def get_dst(options_json: dict) -> dict:
            dst = lj_output_project_name_input.get_value()
            if dst is None or dst == "":
                return []
            # if dst[0] == "[":
            #     dst = json.loads(dst)
            # else:
            #     dst = [dst.strip("'\"")]
            else:
                dst = [dst]
            return dst

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return saved_settings

        def _set_settings_from_json(settings: dict):
            lj_utils.set_settings_from_json(
                settings,
                lj_description_title_input,
                lj_description_title_preview,
                lj_description_readme_editor,
                lj_description_description_editor,
                lj_members_reviewer_selector,
                lj_members_reviewer_preview,
                lj_members_labelers_list,
                lj_members_labelers_list_preview,
                lj_settings_classes_list_widget,
                lj_settings_classes_list_preview,
                lj_settings_tags_list_widget,
                lj_settings_tags_list_preview,
                lj_output_project_name_input,
                lj_output_dataset_keep_checkbox,
                lj_output_dataset_name_input,
                lj_output_project_name_preview,
                lj_output_dataset_name_preview,
            )
            _save_classes_list_settings()
            _save_tags_list_settings()
            _save_settings()
            return

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = create_settings_options(
                lj_description_container,
                lj_description_sidebar_container,
                lj_description_title_preview,
                lj_members_container,
                lj_members_sidebar_container,
                lj_members_preview_container,
                lj_settings_classes_list_edit_container,
                lj_settings_classes_list_widgets_container,
                lj_settings_classes_list_preview,
                lj_settings_tags_list_edit_container,
                lj_settings_tags_list_widgets_container,
                lj_settings_tags_list_preview,
                lj_output_edit_container,
                lj_output_sidebar_container,
                lj_output_container_preview,
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
            get_dst=get_dst,
            data_changed_cb=data_changed_cb,
            need_preview=False,
        )

    @classmethod
    def create_outputs(cls):
        return []
