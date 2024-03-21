from supervisely.app.widgets import (
    Button,
    Container,
    Flexbox,
    Text,
    Field,
    MatchTagMetas,
    NotificationBox,
)
from src.ui.widgets import TagsList, TagsListPreview
from src.ui.dtl.utils import (
    get_set_settings_button_style,
    get_set_settings_container,
    create_save_btn,
    create_set_default_btn,
    get_text_font_size,
)


def create_tags_selector_widgets() -> tuple:
    # match_tag_metas_widget = MatchTagMetas()
    # match_tag_metas_widget.hide()

    tags_list_widget_notification = NotificationBox(
        title="No tags",
        description="Connect to deployed model to display tags.",
    )
    tags_list_widget = TagsList(multiple=True, empty_notification=tags_list_widget_notification)
    tags_list_preview = TagsListPreview(empty_text="No tags selected")
    tags_list_preview.hide()

    tags_list_save_btn = create_save_btn()
    tags_list_set_default_btn = create_set_default_btn()
    tags_list_widget_field = Field(
        content=tags_list_widget,
        title="Model Tags",
        description="Select tags from model",
    )
    tags_list_widgets_container = Container(
        widgets=[
            tags_list_widget_field,
            Flexbox(
                widgets=[
                    tags_list_save_btn,
                    tags_list_set_default_btn,
                ],
                gap=110,
            ),
        ]
    )

    tags_list_edit_text = Text("Model Tags", status="text", font_size=get_text_font_size())
    tags_list_edit_btn = Button(
        text="EDIT",
        icon="zmdi zmdi-edit",
        button_type="text",
        button_size="small",
        emit_on_click="openSidebar",
        style=get_set_settings_button_style(),
    )
    tags_list_edit_container = get_set_settings_container(tags_list_edit_text, tags_list_edit_btn)
    tags_list_edit_container.hide()

    tags_separator = Text("<hr>")
    tags_separator.hide()
    return (
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
    )
