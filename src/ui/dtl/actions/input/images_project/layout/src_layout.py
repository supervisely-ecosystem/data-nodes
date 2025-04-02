from supervisely.app.widgets import Button, NodesFlow


def create_src_options(
    src_input_data_sidebar_layout_container,
    src_input_data_sidebar_widgets_container,
    src_input_data_sidebar_preview_widget,
):
    src_options = [
        NodesFlow.Node.Option(
            name="Select Project",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=src_input_data_sidebar_layout_container,
                sidebar_component=NodesFlow.WidgetOptionComponent(
                    src_input_data_sidebar_widgets_container
                ),
                sidebar_width=350,
            ),
        ),
        NodesFlow.Node.Option(
            name="Source Preview",
            option_component=NodesFlow.WidgetOptionComponent(src_input_data_sidebar_preview_widget),
        ),
    ]
    return src_options


def create_settings_options(
    src_classes_edit_contaniner,
    src_classes_widgets_container,
    src_classes_preview,
    src_tags_edit_contaniner,
    src_tags_widgets_container,
    src_tags_preview,
):
    settings_options = [
        NodesFlow.Node.Option(
            name="Set Classes",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=src_classes_edit_contaniner,
                sidebar_component=NodesFlow.WidgetOptionComponent(src_classes_widgets_container),
                sidebar_width=630,
            ),
        ),
        NodesFlow.Node.Option(
            name="Classes Preview",
            option_component=NodesFlow.WidgetOptionComponent(src_classes_preview),
        ),
        NodesFlow.Node.Option(
            name="Set Tags",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=src_tags_edit_contaniner,
                sidebar_component=NodesFlow.WidgetOptionComponent(src_tags_widgets_container),
                sidebar_width=870,
            ),
        ),
        NodesFlow.Node.Option(
            name="Tags Preview",
            option_component=NodesFlow.WidgetOptionComponent(src_tags_preview),
        ),
    ]
    return settings_options
