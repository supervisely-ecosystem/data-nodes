from supervisely.app.widgets import (
    Container,
    NodesFlow,
    NotificationBox,
    Button,
    Text,
    DatasetThumbnail,
)
from src.ui.widgets import ClassesListPreview, TagsListPreview
from src.ui.dtl.utils import get_set_settings_button_style


def create_preview_button_widget() -> Button:
    ### UPDATE PREVIEW BUTTON
    update_preview_btn = Button(
        text="Update",
        icon="zmdi zmdi-refresh",
        button_type="text",
        button_size="small",
        style=get_set_settings_button_style(),
    )
    update_preview_btn.disable()
    ### -----------------------------
    return update_preview_btn


def create_connect_notification_widget() -> NotificationBox:
    ### CONNECT TO MODEL NOTIFICATION
    connect_notification = NotificationBox(
        title="Connect to deployed model",
        description="to select classes, tags and inference settings",
        box_type="info",
    )
    ### -----------------------------
    return connect_notification


def create_layout(
    lj_selector_layout_container: Container,
    lj_selector_sidebar_container: Container,
    lj_selector_preview_lj_text: Text,
    lj_selector_preview_lj_status: Text,
    lj_selector_preview_lj_progress: Text,
    lj_selector_preview_lj_dataset_thumbnail: DatasetThumbnail,
    lj_selector_preview_classes_text: Text,
    lj_selector_preview_classes: ClassesListPreview,
    lj_selector_preview_tags_text: Text,
    lj_selector_preview_tags: TagsListPreview,
):
    src_options = [
        NodesFlow.Node.Option(
            name="Select Job",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=lj_selector_layout_container,
                sidebar_component=NodesFlow.WidgetOptionComponent(lj_selector_sidebar_container),
                sidebar_width=300,
            ),
        ),
        NodesFlow.Node.Option(
            name="Job Project Thumbnail Preview",
            option_component=NodesFlow.WidgetOptionComponent(
                lj_selector_preview_lj_dataset_thumbnail
            ),
        ),
        NodesFlow.Node.Option(
            name="Job Name Preview",
            option_component=NodesFlow.WidgetOptionComponent(lj_selector_preview_lj_text),
        ),
        NodesFlow.Node.Option(
            name="Job Status Preview",
            option_component=NodesFlow.WidgetOptionComponent(lj_selector_preview_lj_status),
        ),
        NodesFlow.Node.Option(
            name="Job Progress Preview",
            option_component=NodesFlow.WidgetOptionComponent(lj_selector_preview_lj_progress),
        ),
    ]
    settings_options = [
        NodesFlow.Node.Option(
            name="Classes Preview Text",
            option_component=NodesFlow.WidgetOptionComponent(lj_selector_preview_classes_text),
        ),
        NodesFlow.Node.Option(
            name="Classes Preview",
            option_component=NodesFlow.WidgetOptionComponent(lj_selector_preview_classes),
        ),
        NodesFlow.Node.Option(
            name=f"Classes separator",
            option_component=NodesFlow.HtmlOptionComponent("<hr>"),
        ),
        NodesFlow.Node.Option(
            name="Tags Preview Text",
            option_component=NodesFlow.WidgetOptionComponent(lj_selector_preview_tags_text),
        ),
        NodesFlow.Node.Option(
            name="Tags Preview",
            option_component=NodesFlow.WidgetOptionComponent(lj_selector_preview_tags),
        ),
    ]
    return {"src": src_options, "dst": [], "settings": settings_options}
