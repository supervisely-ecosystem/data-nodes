from typing import List
from supervisely.app.widgets import (
    Button,
    Input,
    Text,
    Checkbox,
    Select,
    TextArea,
    NotificationBox,
)
from src.ui.widgets import (
    ClassesList,
    ClassesListPreview,
    TagsList,
    TagsListPreview,
    MembersList,
    MembersListPreview,
)
from src.ui.dtl.utils import (
    set_classes_list_settings_from_json,
    set_classes_list_preview,
    set_tags_list_settings_from_json,
    set_tags_list_preview,
    set_members_list_settings_from_json,
    set_members_list_preview,
)


# SET PREVIEWS
def set_lj_name_preview(lj_description_title_input: Input, lj_description_title_preview: Text):
    name = lj_description_title_input.get_value()
    if name is None or name == "":
        lj_description_title_preview.set("Set description in settings", "text")
    else:
        lj_description_title_preview.set(f"Title: {name}", "text")


def set_lj_reviewer_preview(
    lj_members_reviewer_selector: Select, lj_members_reviewer_preview: Text
):
    reviewer_login = lj_members_reviewer_selector.get_label()
    if reviewer_login is None:
        formatted_login = "select reviewer in settings"
    else:
        # formatted_login = f"<b>{reviewer_login}</b>"
        formatted_login = f'<i class="zmdi zmdi-account" style="color: rgb(132, 146, 166)"></i><span style="padding-left: 5px"><b>{reviewer_login}</b></span>'
    lj_members_reviewer_preview.set(f"Reviewer: {formatted_login}", "text")


def set_lj_output_project_name_preview(
    lj_output_project_name_input: Input, lj_output_project_name_preview: Text
):
    project_name = lj_output_project_name_input.get_value()
    lj_output_project_name_preview.set(
        f"<span style='padding-left: 14px'>Project name: {project_name}</span>", "text"
    )


def set_lj_output_dataset_name_preview(
    lj_output_dataset_name_input: Input,
    lj_output_dataset_keep_checkbox: Checkbox,
    lj_output_dataset_name_preview: Text,
):
    keep_dataset = lj_output_dataset_keep_checkbox.is_checked()
    if keep_dataset:
        lj_output_dataset_name_preview.set(
            "<span style='padding-left: 14px'>Keep source datasets structure</span>",
            "text",
        )
    else:
        dataset_name = lj_output_dataset_name_input.get_value()
        lj_output_dataset_name_preview.set(
            f"<span style='padding-left: 14px'>Dataset name: {dataset_name}</span>", "text"
        )


def set_output_preview(
    modifies_data: bool,
    lj_output_edit_btn: Button,
    lj_output_modifies_data_preview: NotificationBox,
    lj_output_project_name_preview: Text,
    lj_output_dataset_name_preview: Text,
):
    if modifies_data:
        # show output options
        lj_output_modifies_data_preview.hide()
        lj_output_edit_btn.enable()
        lj_output_project_name_preview.show()
        lj_output_dataset_name_preview.show()
    else:
        # hide output options, show notification
        lj_output_edit_btn.disable()
        lj_output_project_name_preview.hide()
        lj_output_dataset_name_preview.hide()
        lj_output_modifies_data_preview.show()


# ----------------------------


# SETTINGS
def save_settings(
    # lj_dataset_selector: SelectDataset
    lj_description_title_input: Input,
    lj_description_readme_editor: TextArea,
    lj_description_description_editor: TextArea,
    lj_members_reviewer_selector: Select,
    lj_members_labelers_selector: MembersList,
    saved_classes_settings: List[str],
    saved_tags_settings: List[str],
    lj_output_project_name_input: Input,
    lj_output_dataset_keep_checkbox: Checkbox,
    lj_output_dataset_name_input: Input,
    modifies_data: bool,
) -> dict:
    name = lj_description_title_input.get_value()
    description = lj_description_description_editor.get_value()
    readme = lj_description_readme_editor.get_value()

    user_ids = [user.id for user in lj_members_labelers_selector.get_selected_members()]
    if not isinstance(user_ids, list):
        user_ids = [user_ids]

    reviewer_id = lj_members_reviewer_selector.get_value()
    project_name = lj_output_project_name_input.get_value()

    if not modifies_data:
        dataset_name = None
        keep_original_ds = True
    else:
        keep_original_ds = lj_output_dataset_keep_checkbox.is_checked()
        if keep_original_ds:
            dataset_name = None
        else:
            dataset_name = lj_output_dataset_name_input.get_value()

    return {
        # description
        "job_name": name,
        "description": description,
        "readme": readme,
        # members
        "user_ids": user_ids,
        "reviewer_id": reviewer_id,
        # classes
        "classes_to_label": saved_classes_settings,
        # tags
        "tags_to_label": saved_tags_settings,
        # output
        "create_new_project": modifies_data,
        "project_name": project_name,
        "dataset_name": dataset_name,
        "keep_original_ds": keep_original_ds,
    }


# ----------------------------


# SET SETTINGS FROM JSON
def set_lj_name_from_json(settings: dict, lj_description_title_input: Input):
    name = settings.get("job_name", "Labeling Job")
    lj_description_title_input.set_value(name)


def set_lj_readme_from_json(settings: dict, lj_description_readme_editor: TextArea):
    readme = settings.get("readme", None)
    lj_description_readme_editor.set_value(readme)


def set_lj_description_from_json(settings: dict, lj_description_description_editor: TextArea):
    description = settings.get("description", None)
    lj_description_description_editor.set_value(description)


def set_lj_reviewer_from_json(settings: dict, lj_members_reviewer_selector: Select):
    reviewer_id = settings.get("reviewer_id", None)
    lj_members_reviewer_selector.set_value(reviewer_id)


def set_output_project_name_from_json(settings: dict, lj_output_project_name_input: Input):
    project_name = settings.get("project_name", "")
    lj_output_project_name_input.set_value(project_name)


def set_output_dataset_name_from_json(
    settings: dict,
    lj_output_dataset_name_input: Input,
    lj_output_dataset_keep_checkbox: Checkbox,
):
    keep_original_ds = settings.get("keep_original_ds", False)
    if keep_original_ds:
        lj_output_dataset_name_input.hide()
        lj_output_dataset_keep_checkbox.check()
    else:
        lj_output_dataset_name_input.show()
        lj_output_dataset_keep_checkbox.uncheck()
    dataset_name = settings.get("dataset_name", "")
    lj_output_dataset_name_input.set_value(dataset_name)


def set_settings_from_json(
    settings: dict,
    lj_description_title_input: Input,
    lj_description_title_preview: Text,
    lj_description_readme_editor: TextArea,
    lj_description_description_editor: TextArea,
    lj_members_reviewer_selector: Select,
    lj_members_reviewer_preview: Text,
    lj_members_labelers_selector: MembersList,
    lj_members_labelers_preview: MembersListPreview,
    lj_settings_classes_list_widget: ClassesList,
    lj_settings_classes_list_preview: ClassesListPreview,
    lj_settings_tags_list_widget: TagsList,
    lj_settings_tags_list_preview: TagsListPreview,
    lj_output_project_name_input: Input,
    lj_output_dataset_keep_checkbox: Checkbox,
    lj_output_dataset_name_input: Input,
    lj_output_project_name_preview: Text,
    lj_output_dataset_name_preview: Text,
) -> dict:
    # SET DESCRIPTION
    set_lj_name_from_json(settings, lj_description_title_input)
    set_lj_readme_from_json(settings, lj_description_readme_editor)
    set_lj_description_from_json(settings, lj_description_description_editor)

    set_lj_name_preview(lj_description_title_input, lj_description_title_preview)
    # ----------------------------

    # SET MEMBERS
    ## reviewer
    set_lj_reviewer_from_json(settings, lj_members_reviewer_selector)
    set_lj_reviewer_preview(lj_members_reviewer_selector, lj_members_reviewer_preview)

    ## labelers
    members_settings = settings.get("user_ids", [])
    set_members_list_settings_from_json(lj_members_labelers_selector, members_settings)
    set_members_list_preview(
        lj_members_labelers_selector, lj_members_labelers_preview, members_settings
    )
    # ----------------------------

    # SET CLASSES
    classes_settings = settings.get("classes_to_label", [])
    set_classes_list_settings_from_json(lj_settings_classes_list_widget, classes_settings)
    set_classes_list_preview(
        lj_settings_classes_list_widget, lj_settings_classes_list_preview, classes_settings
    )
    # ----------------------------

    # SET TAGS
    tags_settings = settings.get("tags_to_label", [])
    set_tags_list_settings_from_json(lj_settings_tags_list_widget, tags_settings)
    set_tags_list_preview(
        lj_settings_tags_list_widget, lj_settings_tags_list_preview, tags_settings
    )
    # ----------------------------

    # SET OUTPUT
    set_output_project_name_from_json(settings, lj_output_project_name_input)
    set_output_dataset_name_from_json(
        settings, lj_output_dataset_name_input, lj_output_dataset_keep_checkbox
    )

    set_lj_output_project_name_preview(lj_output_project_name_input, lj_output_project_name_preview)
    set_lj_output_dataset_name_preview(
        lj_output_dataset_name_input,
        lj_output_dataset_keep_checkbox,
        lj_output_dataset_name_preview,
    )
    # ----------------------------


# ----------------------------
