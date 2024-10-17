from copy import deepcopy
from os.path import dirname, realpath
from typing import List, Optional

import src.globals as g
import src.utils as utils
from src.ui.dtl import SourceAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import (
    classes_list_settings_changed_meta,
    classes_list_to_mapping,
    get_classes_list_value,
    get_layer_docs,
    get_set_settings_button_style,
    get_tags_list_value,
    mapping_to_list,
    set_classes_list_preview,
    set_classes_list_settings_from_json,
    set_tags_list_preview,
    set_tags_list_settings_from_json,
    tags_list_settings_changed_meta,
    tags_list_to_mapping,
)
from supervisely.app.content import StateJson
from src.ui.dtl.actions.input.images_project.layout.src_classes import (
    create_classes_selector_widgets,
)
from src.ui.dtl.actions.input.images_project.layout.src_input_data import (
    create_input_data_selector_widgets,
)
from src.ui.dtl.actions.input.images_project.layout.src_layout import (
    create_settings_options,
    create_src_options,
)
from src.ui.dtl.actions.input.images_project.layout.src_tags import create_tags_selector_widgets
from supervisely import ProjectMeta
from supervisely.app.widgets import Button


class ImagesProjectAction(SourceAction):
    name = "images_project"
    legacy_name = "data"
    title = "Images Project"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/data-layers/data"
    description = "Use to specify project and its datasets that will participate in data transformation process."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_inputs(self):
        return []

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        # Layer Settings
        saved_src = []
        _current_info = None
        _current_meta = ProjectMeta()

        all_ds_map = {}

        default_classes_mapping_settings = "default"
        saved_classes_mapping_settings = "default"

        default_tags_mapping_settings = "default"
        saved_tags_mapping_settings = "default"
        # ----------------------------

        # Project/Dataset Selector
        (
            # Sidebar
            src_input_data_sidebar_dataset_selector,
            src_input_data_sidebar_save_btn,
            src_input_data_sidebar_refresh_btn,
            src_input_data_sidebar_empty_ds_notification,
            src_input_data_sidebar_widgets_container,
            # Preview
            src_input_data_sidebar_preview_widget_text,
            src_input_data_sidebar_preview_widget_pr_thumbnail,
            src_input_data_sidebar_preview_widget_ds_thumbnail,
            src_input_data_sidebar_preview_widget,
            # Layout
            src_input_data_sidebar_layout_text,
            src_input_data_sidebar_layout_select_btn,
            src_input_data_sidebar_layout_container,
        ) = create_input_data_selector_widgets()
        # ----------------------------

        # Classes Selector
        (
            # Sidebar
            src_classes_widget,
            src_classes_save_btn,
            src_classes_set_default_btn,
            src_classes_field,
            src_classes_widgets_container,
            # Preview
            src_classes_preview,
            # Layout
            src_classes_edit_text,
            src_classes_edit_btn,
            src_classes_edit_contaniner,
        ) = create_classes_selector_widgets()
        # ----------------------------

        # TAGS
        (
            # Sidebar
            src_tags_widget,
            src_tags_save_btn,
            src_tags_set_default_btn,
            src_tags_field,
            src_tags_widgets_container,
            # Preview
            src_tags_preview,
            # Layout
            src_tags_edit_text,
            src_tags_edit_btn,
            src_tags_edit_contaniner,
        ) = create_tags_selector_widgets()
        # ----------------------------

        # Update Preview Button
        update_preview_btn = Button(
            text="Update",
            icon="zmdi zmdi-refresh",
            button_type="text",
            button_size="small",
            style=get_set_settings_button_style(),
        )
        update_preview_btn.disable()

        # Refresh project on SELECT
        @src_input_data_sidebar_refresh_btn.click
        def src_input_data_sidebar_refresh_btn_btn_cb():
            # Get currently selected project and datasets
            current_project = src_input_data_sidebar_dataset_selector.get_selected_project_id()
            current_datasets = src_input_data_sidebar_dataset_selector.get_selected_ids()

            # Refresh project list and set current project and datasets if any
            src_input_data_sidebar_dataset_selector.set_workspace_id(g.WORKSPACE_ID)
            src_input_data_sidebar_dataset_selector.set_project_id(current_project)
            src_input_data_sidebar_dataset_selector.set_dataset_ids(current_datasets or [])

        def _set_src_preview():
            src_preview_text = ""
            if _current_info is not None:
                all_datasets = g.api.dataset.get_list(_current_info.id, recursive=True)
                if not len(all_datasets) == len(saved_src):
                    # fix later
                    if len(saved_src) == 1:
                        if saved_src[0].endswith("/*"):
                            src_preview_text = ""
                    else:
                        src_preview_text = utils.generate_src_ds_preview(saved_src, all_ds_map)
            if _current_info is not None:
                if not src_preview_text == "":
                    src_input_data_sidebar_preview_widget_text.show()

                if len(saved_src) == 1:
                    if saved_src[0].endswith("/*"):
                        src_input_data_sidebar_preview_widget_ds_thumbnail.hide()
                        src_input_data_sidebar_preview_widget_pr_thumbnail.show()
                        src_input_data_sidebar_preview_widget_pr_thumbnail.set(_current_info)
                    else:
                        current_ds_info = all_ds_map[saved_src[0]]

                        src_input_data_sidebar_preview_widget_pr_thumbnail.hide()
                        src_input_data_sidebar_preview_widget_ds_thumbnail.show()
                        src_input_data_sidebar_preview_widget_ds_thumbnail.set(
                            _current_info, current_ds_info
                        )
                else:
                    src_input_data_sidebar_preview_widget_ds_thumbnail.hide()
                    src_input_data_sidebar_preview_widget_pr_thumbnail.show()
                    src_input_data_sidebar_preview_widget_pr_thumbnail.set(_current_info)
                src_input_data_sidebar_preview_widget_text.set(src_preview_text, "text")

        def _save_src():
            def read_src_from_widget():
                def _count_all_datasets(data):
                    count = len(data)
                    for ds_info, children in data.items():
                        if children:
                            count += _count_all_datasets(children)
                    return count

                def _get_selected_ds_paths(data, ids: List[int], current_path) -> List[str]:
                    paths = []
                    for ds_info, children in data.items():
                        new_path = current_path + [ds_info.name]
                        full_path_str = "/".join(new_path)

                        if ds_info.id in ids:
                            paths.append(full_path_str)
                        if children:
                            paths.extend(_get_selected_ds_paths(children, ids, new_path))

                    return paths

                def _get_all_ds_mapping(data, current_path):
                    mapping = {}
                    for ds_info, children in data.items():
                        new_path = current_path + [ds_info.name]
                        full_path_str = "/".join(new_path)

                        mapping[full_path_str] = ds_info
                        if children:
                            mapping.update(_get_all_ds_mapping(children, new_path))
                    return mapping

                nonlocal all_ds_map
                # get_list and compare ids
                project_id = src_input_data_sidebar_dataset_selector.get_selected_project_id()
                if project_id is None:
                    return None, []

                project_info = g.api.project.get_info_by_id(project_id)
                if project_info is None:
                    return None, []
                project_name = project_info.name
                dataset_tree = g.api.dataset.get_tree(project_id)

                selected_dataset_ids = src_input_data_sidebar_dataset_selector.get_selected_ids()
                if not selected_dataset_ids:
                    selected_dataset_ids = []

                all_ds_map = {}
                all_ds_count = _count_all_datasets(dataset_tree)
                selected_ds_paths = _get_selected_ds_paths(
                    dataset_tree, selected_dataset_ids, [project_name]
                )

                if all_ds_count == len(selected_ds_paths):
                    return project_info, [f"{project_name}/*"]

                all_ds_map = _get_all_ds_mapping(dataset_tree, [project_name])
                return project_info, selected_ds_paths

            nonlocal _current_info, saved_src
            _current_info, saved_src = read_src_from_widget()
            if len(saved_src) > 0:
                g.current_srcs[layer_id] = saved_src
            utils.clean_current_srcs()

        def _get_classes_mapping_value():
            nonlocal _current_meta
            classes = get_classes_list_value(src_classes_widget, multiple=True)
            all_classes = [oc.name for oc in _current_meta.obj_classes]
            return classes_list_to_mapping(
                selected_classes=classes,
                all_classes=all_classes,
                other="ignore",
                default_allowed=True,
            )

        def _get_tags_mapping_value():
            nonlocal _current_meta
            tags = get_tags_list_value(src_tags_widget, multiple=True)
            all_tags = [oc.name for oc in _current_meta.tag_metas]
            return classes_list_to_mapping(
                selected_classes=tags,
                all_classes=all_tags,
                other="ignore",
                default_allowed=True,
            )

        def _set_classes_mapping_preview():
            set_classes_list_preview(
                src_classes_widget,
                src_classes_preview,
                (
                    saved_classes_mapping_settings
                    if saved_classes_mapping_settings == "default"
                    else mapping_to_list(saved_classes_mapping_settings)
                ),
                src_classes_edit_text,
            )

        def _set_tags_mapping_preview():
            set_tags_list_preview(
                src_tags_widget,
                src_tags_preview,
                (
                    saved_tags_mapping_settings
                    if saved_tags_mapping_settings == "default"
                    else mapping_to_list(saved_tags_mapping_settings)
                ),
                src_tags_edit_text,
            )

        def _save_classes_mapping_setting():
            # save setting to var
            nonlocal saved_classes_mapping_settings
            saved_classes_mapping_settings = _get_classes_mapping_value()

        def _save_tags_mapping_setting():
            nonlocal saved_tags_mapping_settings
            saved_tags_mapping_settings = _get_tags_mapping_value()

        def _set_default_classes_mapping_setting():
            # save setting to var
            nonlocal saved_classes_mapping_settings
            saved_classes_mapping_settings = deepcopy(default_classes_mapping_settings)

        def _set_default_tags_mapping_setting():
            # save setting to var
            nonlocal saved_tags_mapping_settings
            saved_tags_mapping_settings = deepcopy(default_tags_mapping_settings)

        def data_changed_cb(**kwargs):
            project_meta = kwargs.get("project_meta", None)
            if project_meta is None:
                return
            nonlocal _current_info, _current_meta

            if _current_info is not None and len(project_meta.obj_classes) == 0:
                src_classes_edit_text.set("Project has no object classes", "text")
                src_classes_edit_btn.disable()

            if _current_info is not None and len(project_meta.tag_metas) == 0:
                src_tags_edit_text.set("Project has no tags", "text")
                src_tags_edit_btn.disable()

            if project_meta == _current_meta:
                return
            _current_meta = project_meta
            src_classes_widget.loading = True
            new_obj_classes = [cls for cls in project_meta.obj_classes]
            new_class_names = [oc.name for oc in new_obj_classes]

            src_tags_widget.loading = True
            new_tag_metas = [tag for tag in project_meta.tag_metas]
            new_tag_names = [tag.name for tag in new_tag_metas]

            # set classes to widget
            if _current_info is None:
                src_classes_widget.set_project_meta(project_meta)
            else:
                src_classes_widget.read_project_from_id(_current_info.id)

            # update settings according to new meta
            nonlocal saved_classes_mapping_settings, saved_tags_mapping_settings
            if saved_classes_mapping_settings != "default":
                current_classes_list = mapping_to_list(saved_classes_mapping_settings)
                classes_list = classes_list_settings_changed_meta(
                    current_classes_list,
                    new_obj_classes,
                )
                saved_classes_mapping_settings = classes_list_to_mapping(
                    classes_list,
                    new_class_names,
                    other="ignore",
                    default_allowed=False,
                )

            if _current_info is None:
                src_tags_widget.set_project_meta(project_meta)
            else:
                src_tags_widget.read_project_from_id(_current_info.id)

            if saved_tags_mapping_settings != "default":
                current_tags_list = mapping_to_list(saved_tags_mapping_settings)
                tags_list = tags_list_settings_changed_meta(
                    current_tags_list,
                    new_tag_metas,
                )
                saved_tags_mapping_settings = tags_list_to_mapping(
                    tags_list,
                    new_tag_names,
                    other="ignore",
                    default_allowed=False,
                )

            set_classes_list_settings_from_json(
                classes_list_widget=src_classes_widget,
                settings=(
                    new_class_names
                    if saved_classes_mapping_settings == "default"
                    else mapping_to_list(saved_classes_mapping_settings)
                ),
            )
            _set_classes_mapping_preview()

            set_tags_list_settings_from_json(
                tags_list_widget=src_tags_widget,
                settings=(
                    new_tag_names
                    if saved_tags_mapping_settings == "default"
                    else mapping_to_list(saved_tags_mapping_settings)
                ),
            )
            _set_tags_mapping_preview()

            if isinstance(_current_meta, ProjectMeta):
                if len(_current_meta.obj_classes) > 0:
                    src_classes_edit_btn.enable()
                if len(_current_meta.tag_metas) > 0:
                    src_tags_edit_btn.enable()
                update_preview_btn.enable()

            src_classes_widget.loading = False
            src_tags_widget.loading = False

        def get_src(options_json: dict) -> List[str]:
            return saved_src

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return {
                "classes_mapping": saved_classes_mapping_settings,
                "tags_mapping": saved_tags_mapping_settings,
            }

        def _set_src_from_json(srcs: List[str]):
            nonlocal saved_src
            project_info = None
            project_not_found = False
            if len(srcs) == 0:
                # set empty src to widget
                src_input_data_sidebar_dataset_selector.set_project_id(None)
                src_input_data_sidebar_dataset_selector.set_dataset_ids([])
                # set empty project meta
                project_meta = ProjectMeta()
            else:
                # get all datasets
                first_project_name = None
                datasets = []
                for src in srcs:
                    project_name, dataset_name = src.split("/")
                    if first_project_name is None:
                        first_project_name = project_name
                    elif first_project_name != project_name:
                        raise RuntimeError("All datasets should be from the same project")

                    try:
                        project_info = utils.get_project_by_name(name=project_name)
                    except:
                        project_not_found = True
                        break
                    if dataset_name == "*":
                        datasets.extend(utils.get_all_datasets(project_info.id))
                    else:
                        datasets.append(utils.get_dataset_by_name(dataset_name, project_info.id))
                if project_not_found is False:
                    # set datasets to widget
                    src_input_data_sidebar_dataset_selector.set_project_id(project_info.id)
                    src_input_data_sidebar_dataset_selector.set_dataset_ids(
                        [ds.id for ds in datasets]
                    )
                    if len(datasets) == project_info.datasets_count:
                        src_input_data_sidebar_dataset_selector._select_dataset.select_all()
                        # src_input_data_sidebar_dataset_selector._all_datasets_checkbox.check()
                    else:
                        pass
                        # src_input_data_sidebar_dataset_selector._all_datasets_checkbox.uncheck()

                    # get project meta
                    project_meta = utils.get_project_meta(project_info.id)
                else:
                    # set empty src to widget
                    src_input_data_sidebar_dataset_selector.set_project_id(None)
                    src_input_data_sidebar_dataset_selector.set_dataset_ids([])
                    project_meta = ProjectMeta()

            selected_datasets = src_input_data_sidebar_dataset_selector.get_selected_ids()
            if selected_datasets:
                src_input_data_sidebar_save_btn.enable()
                src_input_data_sidebar_empty_ds_notification.hide()
            else:
                src_input_data_sidebar_save_btn.disable()
                src_input_data_sidebar_empty_ds_notification.show()

            # save src
            _save_src()
            # set src preview
            _set_src_preview()
            # update meta
            data_changed_cb(**{"project_meta": project_meta})
            if project_info is not None:
                update_preview_btn.enable()

        def _set_settings_from_json(settings: dict):
            # if settings are empty, set default
            src_classes_widget.loading = True
            classes_mapping_settings = settings.get("classes_mapping", "default")
            set_classes_list_settings_from_json(
                classes_list_widget=src_classes_widget,
                settings=(
                    classes_mapping_settings
                    if classes_mapping_settings == "default"
                    else mapping_to_list(classes_mapping_settings)
                ),
            )
            _save_classes_mapping_setting()
            _set_classes_mapping_preview()
            src_classes_widget.loading = False

            src_tags_widget.loading = True
            tags_mapping_settings = settings.get("tags_mapping", "default")

            set_tags_list_settings_from_json(
                tags_list_widget=src_tags_widget,
                settings=(
                    tags_mapping_settings
                    if tags_mapping_settings == "default"
                    else mapping_to_list(tags_mapping_settings)
                ),
            )
            _save_tags_mapping_setting()
            _set_tags_mapping_preview()
            src_tags_widget.loading = False

        @src_input_data_sidebar_save_btn.click
        def src_input_data_sidebar_save_btn_cb():
            selected_dataset_ids = src_input_data_sidebar_dataset_selector.get_selected_ids()
            if (
                selected_dataset_ids is None
                or len(selected_dataset_ids) == 0
                or selected_dataset_ids[0] is None  # ?
            ):
                return
            _temp_info = _current_info
            _save_src()
            _set_src_preview()
            g.updater("metas")
            if _current_info != _temp_info:
                update_preview_btn.enable()
                g.updater(("nodes", layer_id))

        @src_classes_save_btn.click
        def src_classes_save_btn_cb():
            _save_classes_mapping_setting()
            _set_classes_mapping_preview()
            g.updater("metas")

        @src_classes_set_default_btn.click
        def src_classes_set_default_btn_cb():
            _set_default_classes_mapping_setting()

            set_classes_list_settings_from_json(
                classes_list_widget=src_classes_widget,
                settings=(
                    saved_classes_mapping_settings
                    if saved_classes_mapping_settings == "default"
                    else mapping_to_list(saved_classes_mapping_settings)
                ),
            )

            _set_classes_mapping_preview()
            g.updater("metas")

        @src_tags_save_btn.click
        def src_tags_save_btn_cb():
            _save_tags_mapping_setting()
            _set_tags_mapping_preview()
            g.updater("metas")

        @src_tags_set_default_btn.click
        def src_tags_set_default_btn_cb():
            _set_default_tags_mapping_setting()

            set_tags_list_settings_from_json(
                tags_list_widget=src_tags_widget,
                settings=(
                    saved_tags_mapping_settings
                    if saved_tags_mapping_settings == "default"
                    else mapping_to_list(saved_tags_mapping_settings)
                ),
            )

            _set_tags_mapping_preview()
            g.updater("metas")

        @src_input_data_sidebar_dataset_selector.value_changed
        def select_dataset_changed_handler(dataset_ids):
            selected = src_input_data_sidebar_dataset_selector.get_selected_ids()
            if selected is None or len(selected) == 0:
                src_input_data_sidebar_save_btn.disable()
                src_input_data_sidebar_empty_ds_notification.show()
            else:
                src_input_data_sidebar_save_btn.enable()
                src_input_data_sidebar_empty_ds_notification.hide()

        def postprocess_cb():
            nonlocal _current_info
            project_id = src_input_data_sidebar_dataset_selector.get_selected_project_id()
            project_info = g.api.project.get_info_by_id(project_id)
            src_input_data_sidebar_preview_widget_pr_thumbnail.set(project_info)
            _current_info = project_info

        def create_options(src: List[str], dst: List[str], settings: dict) -> dict:
            _set_src_from_json(src)
            _set_settings_from_json(settings)

            src_options = create_src_options(
                src_input_data_sidebar_layout_container,
                src_input_data_sidebar_widgets_container,
                src_input_data_sidebar_preview_widget,
            )
            settings_options = create_settings_options(
                src_classes_edit_contaniner,
                src_classes_widgets_container,
                src_classes_preview,
                src_tags_edit_contaniner,
                src_tags_widgets_container,
                src_tags_preview,
            )
            return {"src": src_options, "dst": [], "settings": settings_options}

        return Layer(
            action=cls,
            id=layer_id,
            create_options=create_options,
            get_src=get_src,
            get_settings=get_settings,
            data_changed_cb=data_changed_cb,
            custom_update_btn=update_preview_btn,
            postprocess_cb=postprocess_cb,
        )
