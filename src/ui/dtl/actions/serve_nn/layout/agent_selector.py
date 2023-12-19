import os
from typing import Optional, List, NamedTuple
from os.path import realpath, dirname
from supervisely.app.widgets import NodesFlow, Input, Text, Select, Table, Button, Container, Field
import pandas as pd

# from supervisely.api.agent_api import AgentInfo
from src.ui.dtl import NeuralNetworkAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs, get_text_font_size
import src.globals as g
from src.ui.dtl.utils import (
    create_save_btn,
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
)


COL_ID = "id".upper()
COL_NAME = "name".upper()
SELECT_AGENT = "select agent".upper()


columns = [
    COL_ID,
    COL_NAME,
    SELECT_AGENT,
]

AGENT_STATUS_RUNNING_ICON = "<i class='zmdi zmdi-circle' style='color: rgb(19, 206, 102);'></i>"
AGENT_STATUS_WAITING_ICON = "<i class='zmdi zmdi-circle' style='color: rgb(225, 75, 15);'></i> "
AGENT_STATUS_OTHER_ICON = "<i class='zmdi zmdi-circle' style='color: rgb(225, 75, 15);'></i> "


def fill_agent_table(table: Table, columns: List[str], agents_list: List[NamedTuple]):
    lines = []
    for agent in agents_list:
        agent_id = agent.id
        agent_name = agent.name

        agent_status = agent.status
        if agent_status == "running":
            agent_status_icon = AGENT_STATUS_RUNNING_ICON
        elif agent_status == "waiting":
            agent_status_icon = AGENT_STATUS_WAITING_ICON
        else:
            agent_status_icon = AGENT_STATUS_OTHER_ICON

        agent_name_with_status = f"{agent_status_icon} {agent_name}"

        lines.append(
            [
                agent_id,
                agent_name_with_status,
                Table.create_button(SELECT_AGENT),
            ]
        )
    df = pd.DataFrame(lines, columns=columns)
    table.read_pandas(df)


def create_agent_selector_widgets():
    # SIDEBAR
    available_agents = g.api.agent.get_list(g.TEAM_ID)  # -> NamedTuple (AgentInfo)
    agent_selector_sidebar_table = Table(
        fixed_cols=len(columns), per_page=100, width="auto", sort_column_id=0, sort_direction="asc"
    )
    fill_agent_table(agent_selector_sidebar_table, columns, available_agents)

    agent_selector_sidebar_field = Field(
        title="Select Agent",
        description="Select agent to serve the model. If you don't have any agents, please deploy one",
        content=agent_selector_sidebar_table,
    )

    agent_selector_sidebar_save_btn = create_save_btn()
    agent_selector_sidebar_container = Container(
        [
            agent_selector_sidebar_field,
            agent_selector_sidebar_save_btn,
        ]
    )
    # ------------------------------

    # PREVIEW
    # TODO: App thumbnail widget
    agent_selector_preview = Text("Selected agent:", status="text", font_size=get_text_font_size())
    # ------------------------------

    # LAYOUT
    agent_selector_layout_edit_text = Text(
        "Select serving app", status="text", font_size=get_text_font_size()
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
        agent_selector_sidebar_table,
        agent_selector_sidebar_field,
        agent_selector_sidebar_save_btn,
        agent_selector_sidebar_container,
        # preview
        agent_selector_preview,
        # layout
        agent_selector_layout_container,
    )
