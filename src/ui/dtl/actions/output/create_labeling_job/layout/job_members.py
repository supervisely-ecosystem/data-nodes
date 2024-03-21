import src.globals as g
from src.ui.dtl.utils import (
    create_save_btn,
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
)
from supervisely.app.widgets import (
    Button,
    Container,
    Text,
    Select,
    Field,
)

import src.globals as g

from src.ui.widgets import MembersList, MembersListPreview


def create_job_members_widgets():
    # SIDEBAR SETTINGS
    team_members = g.api.user.get_team_members(g.TEAM_ID)
    lj_members_items = [Select.Item(value=member.id, label=member.login) for member in team_members]

    lj_members_reviewer_selector = Select(items=lj_members_items, filterable=True, size="small")
    lj_members_reviewer_field = Field(
        title="Select Reviewer",
        description="Select user that will be responsible for reviewing annotations",
        content=lj_members_reviewer_selector,
    )

    lj_members_labelers_list = MembersList(users=team_members, multiple=True)
    lj_members_labelers_field = Field(
        title="Select Annotators",
        description=(
            "Selected user will see new labeling job in status 'Pending'. "
            "You can select multiple users — in this case dataset will be splitted equally."
        ),
        content=lj_members_labelers_list,
    )

    lj_members_save_btn = create_save_btn()
    lj_members_sidebar_container = Container(
        [
            lj_members_reviewer_field,
            lj_members_labelers_field,
            lj_members_save_btn,
        ]
    )
    # ----------------------------

    # LAYOUT
    lj_members_edit_text = Text("Members", status="text", font_size=get_text_font_size())
    lj_members_edit_btn = Button(
        text="EDIT",
        icon="zmdi zmdi-edit",
        button_type="text",
        button_size="small",
        emit_on_click="openSidebar",
        style=get_set_settings_button_style(),
    )
    lj_members_container = get_set_settings_container(lj_members_edit_text, lj_members_edit_btn)
    # ----------------------------

    # PREVIEW
    lj_members_reviewer_preview = Text(
        "Reviewer: select reviewer in settings", status="text", font_size=get_text_font_size()
    )

    lj_members_labelers_list_text_preview = Text(
        "Labelers:", "text", font_size=get_text_font_size()
    )
    lj_members_labelers_list_preview = MembersListPreview(
        users=team_members, empty_text="Select labelers in settings"
    )
    lj_members_preview_container = Container(
        [
            lj_members_reviewer_preview,
            lj_members_labelers_list_text_preview,
            lj_members_labelers_list_preview,
        ]
    )
    # ----------------------------

    return (
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
    )
