from supervisely.app.widgets import NodesFlow, Container, Field, Checkbox, NotificationBox


def create_node_dst_options(
    select_project_edit_container: Container,
    select_project_sidebar_container: Container,
    select_project_preview_container: Container,
):
    dst_options = [
        NodesFlow.Node.Option(
            name="Select Project",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=select_project_edit_container,
                sidebar_component=NodesFlow.WidgetOptionComponent(select_project_sidebar_container),
                sidebar_width=400,
            ),
        ),
        NodesFlow.Node.Option(
            name="Select Project preview",
            option_component=NodesFlow.WidgetOptionComponent(select_project_preview_container),
        ),
    ]
    return dst_options


def create_node_settings_options(
    select_option_field: Field,
    backup_target_project_checkbox: Checkbox,
    backup_target_project_notification: NotificationBox,
):
    settings_options = [
        NodesFlow.Node.Option(
            name="Select Option",
            option_component=NodesFlow.WidgetOptionComponent(select_option_field),
        ),
        NodesFlow.Node.Option(
            name="Backup Target Project Checkbox",
            option_component=NodesFlow.WidgetOptionComponent(backup_target_project_checkbox),
        ),
        NodesFlow.Node.Option(
            name="Backup Target Project Notification",
            option_component=NodesFlow.WidgetOptionComponent(backup_target_project_notification),
        ),
    ]
    return settings_options
