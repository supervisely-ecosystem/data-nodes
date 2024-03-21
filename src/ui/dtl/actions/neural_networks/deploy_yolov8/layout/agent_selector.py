from supervisely.app.widgets import Text, Select, Button, Container, Field, AgentSelector
import src.globals as g

from src.ui.dtl.utils import get_text_font_size
import src.ui.dtl.actions.neural_networks.deploy_yolov8.layout.utils as utils
from src.ui.dtl.utils import (
    create_save_btn,
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
)

AGENT_STATUS_RUNNING_ICON = "<i class='zmdi zmdi-circle' style='color: rgb(19, 206, 102);'></i>"
AGENT_STATUS_WAITING_ICON = "<i class='zmdi zmdi-circle' style='color: rgb(225, 75, 15);'></i> "
AGENT_STATUS_OTHER_ICON = "<i class='zmdi zmdi-circle' style='color: rgb(225, 75, 15);'></i> "


def create_agent_selector_widgets():
    # SIDEBAR
    # AGENT SELECTOR
    available_agents = g.api.agent.get_list_available(g.TEAM_ID, True)
    agent_selector_sidebar_selector = AgentSelector(g.TEAM_ID, show_only_running=True)

    agent_selector_sidebar_selector_empty_message = Text(
        (
            "No agents available. Follow this "
            "<a href='https://developer.supervisely.com/getting-started/connect-your-computer' target='_blank'> "
            "guide</a> to connect your computer to Supervisely."
        ),
        status="text",
    )

    if len(available_agents) > 0:
        agent_selector_sidebar_selector_empty_message.hide()
    else:
        agent_selector_sidebar_selector.hide()

    agent_selector_sidebar_field = Field(
        title="Select Agent",
        description="Select agent to serve the model. If you don't have any agents, please deploy one",
        content=agent_selector_sidebar_selector,
    )

    # DEVICE SELECTOR
    agent_selector_sidebar_device_selector_empty_message = Text("Select agent first", status="text")

    if len(available_agents) > 0:
        agent_selector_sidebar_device_selector_items = utils.get_agent_devices(available_agents[0])
        agent_selector_sidebar_device_selector_empty_message.hide()
    else:
        agent_selector_sidebar_device_selector_items = []

    agent_selector_sidebar_device_selector = Select(agent_selector_sidebar_device_selector_items)
    agent_selector_sidebar_device_selector_field = Field(
        title="Select Device",
        description="Select device to serve the model",
        content=agent_selector_sidebar_device_selector,
    )

    agent_selector_sidebar_save_btn = create_save_btn()
    agent_selector_sidebar_container = Container(
        [
            agent_selector_sidebar_field,
            agent_selector_sidebar_selector_empty_message,
            agent_selector_sidebar_device_selector_field,
            agent_selector_sidebar_device_selector_empty_message,
            agent_selector_sidebar_save_btn,
        ]
    )
    # ------------------------------

    # PREVIEW
    agent_selector_preview = Text("", "text", font_size=get_text_font_size())
    agent_selector_preview.hide()
    # ------------------------------

    # LAYOUT
    agent_selector_layout_edit_text = Text(
        "Select agent", status="text", font_size=get_text_font_size()
    )
    agent_selector_layout_edit_btn = Button(
        text="EDIT",
        icon="zmdi zmdi-edit",
        button_type="text",
        button_size="small",
        emit_on_click="openSidebar",
        style=get_set_settings_button_style(),
    )

    agent_selector_layout_container = get_set_settings_container(
        agent_selector_layout_edit_text, agent_selector_layout_edit_btn
    )
    # ------------------------------

    return (
        # sidebar
        agent_selector_sidebar_selector,
        agent_selector_sidebar_selector_empty_message,
        agent_selector_sidebar_field,
        agent_selector_sidebar_device_selector,
        agent_selector_sidebar_device_selector_empty_message,
        agent_selector_sidebar_save_btn,
        agent_selector_sidebar_device_selector_field,
        agent_selector_sidebar_container,
        # preview
        agent_selector_preview,
        # layout
        agent_selector_layout_edit_text,
        agent_selector_layout_edit_btn,
        agent_selector_layout_container,
    )
