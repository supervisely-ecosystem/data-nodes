from typing import Optional
from os.path import realpath, dirname

import src.globals as g
from supervisely.app.widgets import (
    NodesFlow,
    Text,
    Select,
    SelectProject,
    SelectDataset,
    Button,
    Container,
    Input,
    ProjectThumbnail,
    Field,
    OneOf,
    Empty,
    Checkbox,
    NotificationBox,
)

from supervisely.app.content import StateJson
from supervisely.project.project_meta import ProjectMeta
from src.ui.dtl.utils import (
    get_layer_docs,
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
    create_save_btn,
)
from src.ui.dtl import OutputAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs, get_text_font_size


class AddToExistingProjectAction(OutputAction):
    name = "add_to_existing_project"
    legacy_name = "existing_project"
    title = "Add to Existing Project"
    docs_url = ""
    description = "Save results of data transformations to existing project in current workspace."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None) -> Layer:
        saved_settings = {}
        _saved_meta = None

        # SIDEBAR
        dst_project_selector = SelectProject(
            workspace_id=g.WORKSPACE_ID,
            allowed_types=[g.SUPPORTED_MODALITIES_MAP[g.MODALITY_TYPE]],
            size="small",
        )

        # fix team and workspace for SelectProject widget
        StateJson()[dst_project_selector._ws_selector._team_selector.widget_id][
            "teamId"
        ] = g.TEAM_ID
        StateJson()[dst_project_selector._ws_selector.widget_id]["workspaceId"] = g.WORKSPACE_ID
        dst_project_selector._ws_selector.disable()
        StateJson().send_changes()

        dst_project_selector_field = Field(
            title="Select Destination Project",
            description="Results will be saved to selected project.",
            content=dst_project_selector,
        )

        dst_dataset_options_existing_dataset_selector = SelectDataset(
            compact=True,
            size="small",
            allowed_project_types=[g.SUPPORTED_MODALITIES_MAP[g.MODALITY_TYPE]],
        )
        dst_dataset_options_new_dataset_input = Input(
            placeholder="Enter dataset name", size="small"
        )

        dst_dataset_options_selector_items = [
            Select.Item("new", "New Dataset", dst_dataset_options_new_dataset_input),
            Select.Item(
                "existing", "Existing Dataset", dst_dataset_options_existing_dataset_selector
            ),
            Select.Item("keep", "Keep source structure", Empty()),
        ]
        dst_dataset_options_selector = Select(dst_dataset_options_selector_items, size="small")
        dst_dataset_options_selector_oneof = OneOf(dst_dataset_options_selector)
        dst_dataset_options_selector_text_1 = Text(
            text=(" - Existing Dataset: select dataset from existing project to save results to."),
            color="#7f858e",
            font_size=13,
        )
        dst_dataset_options_selector_text_2 = Text(
            text=(
                " - New Dataset: enter name of new dataset to create in selected existing project."
            ),
            color="#7f858e",
            font_size=13,
        )
        dst_dataset_options_selector_text_3 = Text(
            text=(
                " - Keep source structure: save the results in datasets that repeats the structure of the input project."
            ),
            color="#7f858e",
            font_size=13,
        )
        dst_dataset_options_selector_field = Field(
            title="Select Dataset Options",
            content=Container(
                [
                    dst_dataset_options_selector_text_1,
                    dst_dataset_options_selector_text_2,
                    dst_dataset_options_selector_text_3,
                    dst_dataset_options_selector,
                    dst_dataset_options_selector_oneof,
                ]
            ),
        )

        sidebar_save_button = create_save_btn()

        select_project_warning_notification_box = NotificationBox(
            box_type="warning",
            description="The ProjectMeta of the source project does not match the ProjectMeta of the destination project. By ticking this checkbox, you confirm that you understand and approve the update of the destination project's ProjectMeta.",
        )
        select_project_warning_checkbox = Checkbox("Confirm")
        select_project_warning_container = Container(
            [select_project_warning_notification_box, select_project_warning_checkbox]
        )
        select_project_warning_container.hide()

        sidebar_container = Container(
            [
                dst_project_selector_field,
                dst_dataset_options_selector_field,
                sidebar_save_button,
            ]
        )

        # SIDEBAR CBs
        @dst_project_selector.value_changed
        def on_dst_project_selector_change(project_id):
            dst_dataset_options_existing_dataset_selector.set_project_id(project_id)

        @sidebar_save_button.click
        def on_save_btn_click():
            _save_settings()

        # -----------------------------

        # LAYOUT
        select_project_text = Text("Select Project", status="text", font_size=get_text_font_size())
        select_project_btn = Button(
            text="SELECT",
            icon="zmdi zmdi-folder",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )
        select_project_container = get_set_settings_container(
            select_project_text, select_project_btn
        )
        # -----------------------------

        # PREVIEW
        dst_project_preview = ProjectThumbnail()
        dst_dataset_preview = Text("", "text", font_size=get_text_font_size())
        dst_preview_container = Container([dst_project_preview, dst_dataset_preview])
        dst_preview_container.hide()
        # -----------------------------

        def _update_preview():
            selected_project_id = dst_project_selector.get_selected_id()
            if selected_project_id is not None:
                project_info = g.api.project.get_info_by_id(selected_project_id)
                dst_project_preview.set(project_info)

                dataset_option = dst_dataset_options_selector.get_value()
                if dataset_option == "new":
                    dst_dataset_preview.set(
                        f"Dataset: {dst_dataset_options_new_dataset_input.get_value()}", "text"
                    )
                elif dataset_option == "existing":
                    dataset_name = g.api.dataset.get_info_by_id(
                        dst_dataset_options_existing_dataset_selector.get_selected_id()
                    ).name
                    dst_dataset_preview.set(f"Dataset: {dataset_name}", "text")
                else:
                    dst_dataset_preview.set(
                        "Dataset(s) will keep structure from input project", "text"
                    )
                dst_preview_container.show()

        def get_settings(options_json: dict):
            nonlocal saved_settings
            return {
                **saved_settings,
                "merge_different_meta": select_project_warning_checkbox.is_checked(),
            }

        def _set_settings_from_json(settings: dict):
            dataset_option = settings.get("dataset_option", "new")
            dst_dataset_options_selector.set_value(dataset_option)
            if dataset_option == "new":
                dataset_name = settings.get("dataset_name", "")
                dst_dataset_options_new_dataset_input.set_value(dataset_name)
            elif dataset_option == "existing":
                dataset_id = settings.get("dataset_id", None)
                dst_dataset_options_existing_dataset_selector.set_dataset_id(dataset_id)
            else:
                pass
            _save_settings()

        def project_selected_cb(**kwargs):
            nonlocal _saved_meta
            nonlocal saved_settings

            project_meta = kwargs.get("project_meta", None)

            if _saved_meta is None or project_meta == _saved_meta:
                select_project_warning_container.hide()
            else:
                select_project_warning_container.show()

        def _save_settings():
            nonlocal saved_settings
            nonlocal _saved_meta

            project_id = dst_project_selector.get_selected_id()

            settings = {}
            dataset_options = dst_dataset_options_selector.get_value()
            if dataset_options == "new":
                settings["dataset_option"] = "new"
                settings["dataset_name"] = dst_dataset_options_new_dataset_input.get_value()
            elif dataset_options == "existing":
                settings["dataset_option"] = "existing"
                settings["dataset_id"] = (
                    dst_dataset_options_existing_dataset_selector.get_selected_id()
                )
            else:
                settings["dataset_option"] = "keep"

            if project_id:
                _saved_meta = g.api.project.get_meta(project_id)
                _saved_meta = ProjectMeta.from_json(_saved_meta)
                g.updater("metas")
            else:
                _saved_meta = None

            saved_settings = settings
            _update_preview()

        def get_dst(options_json: dict) -> dict:
            project_id = dst_project_selector.get_selected_id()
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

            dst_project_selector.set_project_id(project_id)
            dst_dataset_options_existing_dataset_selector.set_project_id(project_id)

            _update_preview()

            settings_options = [
                NodesFlow.Node.Option(
                    name="Select Project",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=select_project_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(sidebar_container),
                        sidebar_width=400,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="classes_mapping_preview",
                    option_component=NodesFlow.WidgetOptionComponent(dst_preview_container),
                ),
                NodesFlow.Node.Option(
                    name="Approve Checkbox",
                    option_component=NodesFlow.WidgetOptionComponent(
                        select_project_warning_container
                    ),
                ),
            ]
            return {
                "src": [],
                "dst": [],
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
