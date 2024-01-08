from typing import List
from supervisely.app.widgets import (
    NodesFlow,
    Container,
    Text,
    Checkbox,
)


def create_node_layout(
    agent_selector_layout_container: Container,
    agent_selector_sidebar_container: Container,
    agent_selector_preview: Text,
    model_selector_layout_container: Container,
    model_selector_sidebar_container: Container,
    model_selector_preview: Text,
    model_selector_preview_type: Text,
    model_selector_stop_model_after_pipeline_checkbox: Checkbox,
    model_serve_layout_container: Container,
) -> List[NodesFlow.Node.Option]:
    settings_options = [
        NodesFlow.Node.Option(
            name="Agent Selector",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=agent_selector_layout_container,
                sidebar_component=NodesFlow.WidgetOptionComponent(agent_selector_sidebar_container),
                sidebar_width=420,
            ),
        ),
        NodesFlow.Node.Option(
            name="Agent Selector Preview",
            option_component=NodesFlow.WidgetOptionComponent(agent_selector_preview),
        ),
        NodesFlow.Node.Option(
            name=f"Agent Selector Separator",
            option_component=NodesFlow.HtmlOptionComponent("<hr>"),
        ),
        NodesFlow.Node.Option(
            name="Model Selector",
            option_component=NodesFlow.WidgetOptionComponent(
                widget=model_selector_layout_container,
                sidebar_component=NodesFlow.WidgetOptionComponent(model_selector_sidebar_container),
                sidebar_width=860,
            ),
        ),
        NodesFlow.Node.Option(
            name="Model Selector Type Preview",
            option_component=NodesFlow.WidgetOptionComponent(model_selector_preview_type),
        ),
        NodesFlow.Node.Option(
            name="Model Selector Preview",
            option_component=NodesFlow.WidgetOptionComponent(model_selector_preview),
        ),
        NodesFlow.Node.Option(
            name="Stop Model Checkbox",
            option_component=NodesFlow.WidgetOptionComponent(
                model_selector_stop_model_after_pipeline_checkbox
            ),
        ),
        NodesFlow.Node.Option(
            name=f"Stop Model Separator",
            option_component=NodesFlow.HtmlOptionComponent("<hr>"),
        ),
        NodesFlow.Node.Option(
            name="Serve Model Button",
            option_component=NodesFlow.WidgetOptionComponent(model_serve_layout_container),
        ),
    ]

    return settings_options
