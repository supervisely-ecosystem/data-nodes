from supervisely.app.widgets import NodesFlow, Container, Text
from src.ui.widgets import ClassesListPreview, TagsListPreview


def create_settings_options(
    lj_description_container: Container,
    lj_description_sidebar_container: Container,
    lj_description_title_preview: Text,
    lj_team_container: Container,
    lj_team_sidebar_container: Container,
    lj_team_preview_container: Container,
    lj_settings_classes_list_edit_container: Container,
    lj_settings_classes_list_widgets_container: Container,
    lj_settings_classes_list_preview: ClassesListPreview,
    lj_settings_tags_list_edit_container: Container,
    lj_settings_tags_list_widgets_container: Container,
    lj_settings_tags_list_preview: TagsListPreview,
    lj_output_edit_container: Container,
    lj_output_sidebar_container: Container,
    lj_output_container_preview: Container,
):
    settings_options = [
        NodesFlow.Node.Option(
            name="Job Description",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=lj_description_container,
                sidebar_component=NodesFlow.WidgetOptionComponent(lj_description_sidebar_container),
                sidebar_width=380,
            ),
        ),
        NodesFlow.Node.Option(
            name="Job Description Preview",
            option_component=NodesFlow.WidgetOptionComponent(lj_description_title_preview),
        ),
        NodesFlow.Node.Option(
            name=f"separator info",
            option_component=NodesFlow.HtmlOptionComponent("<hr>"),
        ),
        NodesFlow.Node.Option(
            name="Job Team",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=lj_team_container,
                sidebar_component=NodesFlow.WidgetOptionComponent(lj_team_sidebar_container),
                sidebar_width=380,
            ),
        ),
        NodesFlow.Node.Option(
            name="Job Team Preview",
            option_component=NodesFlow.WidgetOptionComponent(lj_team_preview_container),
        ),
        NodesFlow.Node.Option(
            name=f"separator members",
            option_component=NodesFlow.HtmlOptionComponent("<hr>"),
        ),
        NodesFlow.Node.Option(
            name="Job Classes",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=lj_settings_classes_list_edit_container,
                sidebar_component=NodesFlow.WidgetOptionComponent(
                    lj_settings_classes_list_widgets_container
                ),
                sidebar_width=380,
            ),
        ),
        NodesFlow.Node.Option(
            name="Job Classes Preview",
            option_component=NodesFlow.WidgetOptionComponent(lj_settings_classes_list_preview),
        ),
        NodesFlow.Node.Option(
            name=f"separator classes",
            option_component=NodesFlow.HtmlOptionComponent("<hr>"),
        ),
        NodesFlow.Node.Option(
            name="Job Tags",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=lj_settings_tags_list_edit_container,
                sidebar_component=NodesFlow.WidgetOptionComponent(
                    lj_settings_tags_list_widgets_container
                ),
                sidebar_width=380,
            ),
        ),
        NodesFlow.Node.Option(
            name="Job Tags Preview",
            option_component=NodesFlow.WidgetOptionComponent(lj_settings_tags_list_preview),
        ),
        NodesFlow.Node.Option(
            name=f"separator tags",
            option_component=NodesFlow.HtmlOptionComponent("<hr>"),
        ),
        NodesFlow.Node.Option(
            name="Job Output",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=lj_output_edit_container,
                sidebar_component=NodesFlow.WidgetOptionComponent(lj_output_sidebar_container),
                sidebar_width=380,
            ),
        ),
        NodesFlow.Node.Option(
            name="Job Output Preview",
            option_component=NodesFlow.WidgetOptionComponent(lj_output_container_preview),
        ),
    ]

    return settings_options
