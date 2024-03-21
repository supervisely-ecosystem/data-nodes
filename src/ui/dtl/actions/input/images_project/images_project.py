import copy
from os.path import dirname, realpath
from typing import List, Optional

import src.globals as g
import src.utils as utils
from src.ui.dtl import SourceAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import (
    create_save_btn,
    get_text_font_size,
    get_layer_docs,
    mapping_to_list,
    get_set_settings_button_style,
    get_set_settings_container,
    # classes
    classes_list_to_mapping,
    get_classes_list_value,
    set_classes_list_preview,
    set_classes_list_settings_from_json,
    classes_list_settings_changed_meta,
    # tags
    tags_list_to_mapping,
    get_tags_list_value,
    set_tags_list_preview,
    set_tags_list_settings_from_json,
    tags_list_settings_changed_meta,
)
from src.ui.widgets import ClassesListPreview, TagsListPreview
from supervisely import ProjectMeta, ProjectType
from supervisely.app.content import StateJson
from supervisely.app.widgets import (
    Button,
    Container,
    NodesFlow,
    NotificationBox,
    SelectDataset,
    Text,
    ClassesTable,
    TagsTable,
    ProjectThumbnail,
    Field,
)


# ImagesProject
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
        # Src widgets
        select_datasets = SelectDataset(
            multiselect=True,
            select_all_datasets=True,
            allowed_project_types=[ProjectType.IMAGES],
            compact=False,
        )
        select_datasets_text = Text("Select Project", status="text", font_size=get_text_font_size())
        select_datasets_btn = Button(
            text="SELECT",
            icon="zmdi zmdi-folder",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )
        empty_dataset_notification = NotificationBox(
            title="No datasets selected", description="Select at lease one dataset"
        )
        empty_dataset_notification.hide()
        select_datasets_container = get_set_settings_container(
            select_datasets_text, select_datasets_btn
        )
        src_save_btn = Button(
            "Save", icon="zmdi zmdi-floppy", emit_on_click="save", call_on_click="closeSidebar();"
        )
        src_preview_widget_text = Text("", status="text", font_size=get_text_font_size())
        src_preview_widget_text.hide()
        src_preview_widget_thumbnail = ProjectThumbnail(remove_margins=True)
        src_preview_widget_thumbnail.hide()
        src_preview_widget = Container(
            widgets=[src_preview_widget_thumbnail, src_preview_widget_text]
        )
        src_widgets_container = Container(
            widgets=[select_datasets, empty_dataset_notification, src_save_btn]
        )

        saved_src = []

        # fix team and workspace for SelectDataset widget
        StateJson()[select_datasets._project_selector._ws_selector._team_selector.widget_id][
            "teamId"
        ] = g.TEAM_ID
        StateJson()[select_datasets._project_selector._ws_selector.widget_id][
            "workspaceId"
        ] = g.WORKSPACE_ID
        select_datasets._project_selector._ws_selector.disable()
        StateJson().send_changes()

        # Settings widgets
        _current_info = None
        _current_meta = ProjectMeta()

        # add to sidebar when no project selected
        # empty_src_notification = NotificationBox(
        #     title="No classes",
        #     description="Choose datasets and ensure that source project have classes.",
        # )

        # CLASSES
        classes_mapping_widget = ClassesTable()
        classes_mapping_save_btn = create_save_btn()
        classes_mapping_set_default_btn = Button(
            "Set Default", button_type="info", plain=True, icon="zmdi zmdi-refresh"
        )
        classes_mapping_preview = ClassesListPreview()

        classes_mapping_field = Field(
            content=classes_mapping_widget,
            title="Classes",
            description=(
                "Select classes that will be used in data transformation processes. "
                "If class is not selected, it will be ignored."
            ),
        )
        classes_mapping_widgets_container = Container(
            widgets=[
                classes_mapping_field,
                Container(
                    widgets=[
                        classes_mapping_save_btn,
                        classes_mapping_set_default_btn,
                    ],
                    direction="horizontal",
                    gap=0,
                    fractions=[1, 0],
                    # gap=355,
                ),
            ]
        )
        classes_mapping_edit_text = Text("Classes", status="text", font_size=get_text_font_size())
        classes_mapping_edit_btn = Button(
            text="EDIT",
            icon="zmdi zmdi-edit",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )

        if g.PROJECT_ID is None:
            classes_mapping_edit_btn.disable()

        classes_mapping_edit_contaniner = get_set_settings_container(
            classes_mapping_edit_text, classes_mapping_edit_btn
        )
        # -----

        # TAGS
        tags_mapping_widget = TagsTable()
        tags_mapping_save_btn = create_save_btn()
        tags_mapping_set_default_btn = Button(
            "Set Default", button_type="info", plain=True, icon="zmdi zmdi-refresh"
        )
        tags_mapping_preview = TagsListPreview()

        tags_mapping_field = Field(
            content=tags_mapping_widget,
            title="Tags",
            description=(
                "Select tags that will be used in data transformation processes. "
                "If tag is not selected, it will be ignored."
            ),
        )
        tags_mapping_widgets_container = Container(
            widgets=[
                tags_mapping_field,
                Container(
                    widgets=[
                        tags_mapping_save_btn,
                        tags_mapping_set_default_btn,
                    ],
                    direction="horizontal",
                    gap=0,
                    fractions=[1, 0],
                    # gap=355,
                ),
            ]
        )
        tags_mapping_edit_text = Text("Tags", status="text", font_size=get_text_font_size())
        tags_mapping_edit_btn = Button(
            text="EDIT",
            icon="zmdi zmdi-edit",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )

        if g.PROJECT_ID is None:
            tags_mapping_edit_btn.disable()

        tags_mapping_edit_contaniner = get_set_settings_container(
            tags_mapping_edit_text, tags_mapping_edit_btn
        )

        # -----

        update_preview_btn = Button(
            text="Update",
            icon="zmdi zmdi-refresh",
            button_type="text",
            button_size="small",
            style=get_set_settings_button_style(),
        )
        update_preview_btn.disable()

        default_classes_mapping_settings = "default"
        saved_classes_mapping_settings = "default"

        default_tags_mapping_settings = "default"
        saved_tags_mapping_settings = "default"

        def _set_src_preview():
            src_preview_text = ""
            if _current_info is not None:
                if not _current_info.datasets_count == len(saved_src):
                    # fix later
                    if len(saved_src) == 1:
                        if saved_src[0].endswith("/*"):
                            src_preview_text = ""
                    else:
                        src_preview_text = "".join(
                            f"<li>{src.replace('/', ' / ')}</li>" for src in saved_src
                        )
                        src_preview_text = f'<ul style="margin: 1px; padding: 0px 0px 0px 18px">{src_preview_text}<ul>'
            if _current_info is not None:
                if not src_preview_text == "":
                    src_preview_widget_text.show()
                src_preview_widget_thumbnail.show()
                src_preview_widget_thumbnail.set(_current_info)
                src_preview_widget_text.text = src_preview_text

        def _save_src():
            def read_src_from_widget():
                # get_list and compare ids
                selected_dataset_ids = select_datasets.get_selected_ids()
                project_id = select_datasets.get_selected_project_id()
                datasets = []
                if project_id is not None:
                    datasets = g.api.dataset.get_list(project_id)

                project_info = None
                if (
                    selected_dataset_ids is None
                    or len(selected_dataset_ids) == 0
                    or selected_dataset_ids[0] is None  # ?
                ):
                    selected_dataset_ids = []

                if project_id is not None:
                    project_info = g.api.project.get_info_by_id(project_id)

                dataset_names = []
                for ds in datasets:
                    if ds.id in selected_dataset_ids:
                        dataset_names.append(ds.name)

                if project_info is None:
                    return None, []
                if project_info.datasets_count == len(dataset_names):
                    return project_info, [f"{project_info.name}/*"]
                return project_info, [f"{project_info.name}/{name}" for name in dataset_names]

            nonlocal _current_info, saved_src
            _current_info, saved_src = read_src_from_widget()

        def _get_classes_mapping_value():
            nonlocal _current_meta
            classes = get_classes_list_value(classes_mapping_widget, multiple=True)
            all_classes = [oc.name for oc in _current_meta.obj_classes]
            return classes_list_to_mapping(
                selected_classes=classes,
                all_classes=all_classes,
                other="ignore",
                default_allowed=True,
            )

        def _get_tags_mapping_value():
            nonlocal _current_meta
            tags = get_tags_list_value(tags_mapping_widget, multiple=True)
            all_tags = [oc.name for oc in _current_meta.tag_metas]
            return classes_list_to_mapping(
                selected_classes=tags,
                all_classes=all_tags,
                other="ignore",
                default_allowed=True,
            )

        def _set_classes_mapping_preview():
            set_classes_list_preview(
                classes_mapping_widget,
                classes_mapping_preview,
                (
                    saved_classes_mapping_settings
                    if saved_classes_mapping_settings == "default"
                    else mapping_to_list(saved_classes_mapping_settings)
                ),
                classes_mapping_edit_text,
            )

        def _set_tags_mapping_preview():
            set_tags_list_preview(
                tags_mapping_widget,
                tags_mapping_preview,
                (
                    saved_tags_mapping_settings
                    if saved_tags_mapping_settings == "default"
                    else mapping_to_list(saved_tags_mapping_settings)
                ),
                tags_mapping_edit_text,
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
            saved_classes_mapping_settings = copy.deepcopy(default_classes_mapping_settings)

        def _set_default_tags_mapping_setting():
            # save setting to var
            nonlocal saved_tags_mapping_settings
            saved_tags_mapping_settings = copy.deepcopy(default_tags_mapping_settings)

        def data_changed_cb(**kwargs):
            project_meta = kwargs.get("project_meta", None)
            if project_meta is None:
                return
            nonlocal _current_info, _current_meta

            if _current_info is not None and len(project_meta.obj_classes) == 0:
                classes_mapping_edit_text.set("Project has no object classes", "text")
                classes_mapping_edit_btn.disable()

            if _current_info is not None and len(project_meta.tag_metas) == 0:
                tags_mapping_edit_text.set("Project has no tags", "text")
                tags_mapping_edit_btn.disable()

            if project_meta == _current_meta:
                return
            _current_meta = project_meta
            classes_mapping_widget.loading = True
            new_obj_classes = [cls for cls in project_meta.obj_classes]
            new_class_names = [oc.name for oc in new_obj_classes]

            tags_mapping_widget.loading = True
            new_tag_metas = [tag for tag in project_meta.tag_metas]
            new_tag_names = [tag.name for tag in new_tag_metas]

            # set classes to widget
            if _current_info is None:
                classes_mapping_widget.set_project_meta(project_meta)
            else:
                classes_mapping_widget.read_project_from_id(_current_info.id)

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
                tags_mapping_widget.set_project_meta(project_meta)
            else:
                tags_mapping_widget.read_project_from_id(_current_info.id)

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
                classes_list_widget=classes_mapping_widget,
                settings=(
                    new_class_names
                    if saved_classes_mapping_settings == "default"
                    else mapping_to_list(saved_classes_mapping_settings)
                ),
            )
            _set_classes_mapping_preview()

            set_tags_list_settings_from_json(
                tags_list_widget=tags_mapping_widget,
                settings=(
                    new_tag_names
                    if saved_tags_mapping_settings == "default"
                    else mapping_to_list(saved_tags_mapping_settings)
                ),
            )
            _set_tags_mapping_preview()

            if isinstance(_current_meta, ProjectMeta):
                if len(_current_meta.obj_classes) > 0:
                    classes_mapping_edit_btn.enable()
                if len(_current_meta.tag_metas) > 0:
                    tags_mapping_edit_btn.enable()
                update_preview_btn.enable()

            classes_mapping_widget.loading = False
            tags_mapping_widget.loading = False

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
            if len(srcs) == 0:
                # set empty src to widget
                StateJson()[select_datasets._project_selector.widget_id]["projectId"] = None
                StateJson()[select_datasets.widget_id]["datasets"] = []
                # select_datasets._all_datasets_checkbox.uncheck()
                StateJson().send_changes()

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
                    project_info = utils.get_project_by_name(name=project_name)
                    if dataset_name == "*":
                        datasets.extend(utils.get_all_datasets(project_info.id))
                    else:
                        datasets.append(utils.get_dataset_by_name(dataset_name, project_info.id))

                # set datasets to widget
                StateJson()[select_datasets._project_selector.widget_id][
                    "projectId"
                ] = project_info.id
                StateJson()[select_datasets.widget_id]["datasets"] = [ds.id for ds in datasets]
                if len(datasets) == project_info.datasets_count:
                    select_datasets._all_datasets_checkbox.check()
                else:
                    select_datasets._all_datasets_checkbox.uncheck()
                StateJson().send_changes()

                # get project meta
                project_meta = utils.get_project_meta(project_info.id)

            # save src
            _save_src()
            # set src preview
            _set_src_preview()
            # update meta
            data_changed_cb(**{"project_meta": project_meta})

        def _set_settings_from_json(settings: dict):
            # if settings are empty, set default
            classes_mapping_widget.loading = True
            classes_mapping_settings = settings.get("classes_mapping", "default")
            set_classes_list_settings_from_json(
                classes_list_widget=classes_mapping_widget,
                settings=(
                    classes_mapping_settings
                    if classes_mapping_settings == "default"
                    else mapping_to_list(classes_mapping_settings)
                ),
            )
            _save_classes_mapping_setting()
            _set_classes_mapping_preview()
            classes_mapping_widget.loading = False

            tags_mapping_widget.loading = True
            tags_mapping_settings = settings.get("tags_mapping", "default")

            set_tags_list_settings_from_json(
                tags_list_widget=tags_mapping_widget,
                settings=(
                    tags_mapping_settings
                    if tags_mapping_settings == "default"
                    else mapping_to_list(tags_mapping_settings)
                ),
            )
            _save_tags_mapping_setting()
            _set_tags_mapping_preview()
            tags_mapping_widget.loading = False

        @src_save_btn.click
        def src_save_btn_cb():
            selected_dataset_ids = select_datasets.get_selected_ids()
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

        @classes_mapping_save_btn.click
        def classes_mapping_save_btn_cb():
            _save_classes_mapping_setting()
            _set_classes_mapping_preview()
            g.updater("metas")

        @classes_mapping_set_default_btn.click
        def classes_mapping_set_default_btn_cb():
            _set_default_classes_mapping_setting()

            set_classes_list_settings_from_json(
                classes_list_widget=classes_mapping_widget,
                settings=(
                    saved_classes_mapping_settings
                    if saved_classes_mapping_settings == "default"
                    else mapping_to_list(saved_classes_mapping_settings)
                ),
            )

            _set_classes_mapping_preview()
            g.updater("metas")

        @tags_mapping_save_btn.click
        def tags_mapping_save_btn_cb():
            _save_tags_mapping_setting()
            _set_tags_mapping_preview()
            g.updater("metas")

        @tags_mapping_set_default_btn.click
        def tags_mapping_set_default_btn_cb():
            _set_default_tags_mapping_setting()

            set_tags_list_settings_from_json(
                tags_list_widget=tags_mapping_widget,
                settings=(
                    saved_tags_mapping_settings
                    if saved_tags_mapping_settings == "default"
                    else mapping_to_list(saved_tags_mapping_settings)
                ),
            )

            _set_tags_mapping_preview()
            g.updater("metas")

        @select_datasets.value_changed
        def select_dataset_changed_handler(args):
            selected = select_datasets.get_selected_ids()
            if selected is None or len(selected) == 0:
                src_save_btn.disable()
                empty_dataset_notification.show()
            else:
                src_save_btn.enable()
                empty_dataset_notification.hide()

        def create_options(src: List[str], dst: List[str], settings: dict) -> dict:
            _set_src_from_json(src)
            _set_settings_from_json(settings)

            src_options = [
                NodesFlow.Node.Option(
                    name="Select Project",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=select_datasets_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(src_widgets_container),
                        sidebar_width=300,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="Source Preview",
                    option_component=NodesFlow.WidgetOptionComponent(src_preview_widget),
                ),
            ]
            settings_options = [
                NodesFlow.Node.Option(
                    name="Set Classes",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=classes_mapping_edit_contaniner,
                        sidebar_component=NodesFlow.WidgetOptionComponent(
                            classes_mapping_widgets_container
                        ),
                        sidebar_width=630,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="Classes Preview",
                    option_component=NodesFlow.WidgetOptionComponent(classes_mapping_preview),
                ),
                NodesFlow.Node.Option(
                    name="Set Tags",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=tags_mapping_edit_contaniner,
                        sidebar_component=NodesFlow.WidgetOptionComponent(
                            tags_mapping_widgets_container
                        ),
                        sidebar_width=870,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="Tags Preview",
                    option_component=NodesFlow.WidgetOptionComponent(tags_mapping_preview),
                ),
            ]
            return {"src": src_options, "dst": [], "settings": settings_options}

        return Layer(
            action=cls,
            id=layer_id,
            create_options=create_options,
            get_src=get_src,
            get_settings=get_settings,
            data_changed_cb=data_changed_cb,
            custom_update_btn=update_preview_btn,
        )
