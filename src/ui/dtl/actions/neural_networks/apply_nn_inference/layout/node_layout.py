from supervisely.app.widgets import Container, NodesFlow, NotificationBox, Button, Text
from src.ui.widgets import ClassesListPreview, TagsListPreview
from src.ui.dtl.utils import get_set_settings_button_style


# def create_separators() -> tuple:
#     connect_model_separator = (
#         NodesFlow.Node.Option(
#             name=f"Connect Model Separator",
#             option_component=NodesFlow.HtmlOptionComponent("<hr>"),
#         ),
#     )
#     classes_separator = (
#         NodesFlow.Node.Option(
#             name=f"Classes Separator",
#             option_component=NodesFlow.HtmlOptionComponent("<hr>"),
#         ),
#     )
#     tags_separator = NodesFlow.Node.Option(
#         name=f"Tags Separator",
#         option_component=NodesFlow.HtmlOptionComponent("<hr>"),
#     )


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
    connect_nn_edit_container: Container,
    connect_nn_widgets_container: Container,
    connect_nn_model_preview: Text,
    connect_notification: NotificationBox,
    classes_list_edit_container: Container,
    classes_list_widgets_container: Container,
    classes_list_preview: ClassesListPreview,
    tags_list_edit_container: Container,
    tags_list_widgets_container: Container,
    tags_list_preview: TagsListPreview,
    inf_settings_edit_container: Container,
    inf_settings_widgets_container: Container,
    inf_settings_preview_container: Container,
    model_separator: Text,
    classes_separator: Text,
    tags_separator: Text,
):

    settings_options = [
        NodesFlow.Node.Option(
            name="Connect to Model",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=connect_nn_edit_container,
                sidebar_component=NodesFlow.WidgetOptionComponent(connect_nn_widgets_container),
                sidebar_width=402,
            ),
        ),
        NodesFlow.Node.Option(
            "model_preview",
            option_component=NodesFlow.WidgetOptionComponent(connect_nn_model_preview),
        ),
        NodesFlow.Node.Option(
            "connect_notification",
            option_component=NodesFlow.WidgetOptionComponent(connect_notification),
        ),
        NodesFlow.Node.Option(
            name=f"Connect Model Separator",
            # option_component=NodesFlow.HtmlOptionComponent("<hr>"),
            option_component=NodesFlow.WidgetOptionComponent(model_separator),
        ),
        NodesFlow.Node.Option(
            name="Select Classes",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=classes_list_edit_container,
                sidebar_component=NodesFlow.WidgetOptionComponent(classes_list_widgets_container),
                sidebar_width=380,
            ),
        ),
        NodesFlow.Node.Option(
            "classes_preview",
            option_component=NodesFlow.WidgetOptionComponent(classes_list_preview),
        ),
        NodesFlow.Node.Option(
            name=f"Classes Separator",
            # option_component=NodesFlow.HtmlOptionComponent("<hr>"),
            option_component=NodesFlow.WidgetOptionComponent(classes_separator),
        ),
        NodesFlow.Node.Option(
            name="Select Tags",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=tags_list_edit_container,
                sidebar_component=NodesFlow.WidgetOptionComponent(tags_list_widgets_container),
                sidebar_width=380,
            ),
        ),
        NodesFlow.Node.Option(
            "tags_preview",
            option_component=NodesFlow.WidgetOptionComponent(tags_list_preview),
        ),
        NodesFlow.Node.Option(
            name=f"Tags Separator",
            # option_component=NodesFlow.HtmlOptionComponent("<hr>"),
            option_component=NodesFlow.WidgetOptionComponent(tags_separator),
        ),
        NodesFlow.Node.Option(
            name="Inference Settings",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=inf_settings_edit_container,
                sidebar_component=NodesFlow.WidgetOptionComponent(inf_settings_widgets_container),
                sidebar_width=380,
            ),
        ),
        NodesFlow.Node.Option(
            "inference_settings_preview",
            option_component=NodesFlow.WidgetOptionComponent(inf_settings_preview_container),
        ),
    ]
    return settings_options
