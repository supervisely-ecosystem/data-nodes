import os
from typing import Optional, List
from os.path import realpath, dirname
from supervisely.app.widgets import NodesFlow, Input, Text, Select, Table, Button, Container, Field
from supervisely.api.app_api import AppInfo
import pandas as pd
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
# COL_DESCRIPTION = "description".upper()
SELECT_APP = "select app".upper()


columns = [
    COL_ID,
    COL_NAME,
    # COL_DESCRIPTION,
    SELECT_APP,
]


def fill_apps_table(table: Table, columns: List[str], apps_list: List[AppInfo]):
    lines = []
    for app in apps_list:
        app_id = app.id
        app_name = app.name
        app_description = app.config["description"]

        app_icon = f"<img src={app.config.get('icon')} width=20 height=20>"
        repo_name = app.slug.split("/")[-1]
        app_name_with_link = f"{app_icon} <i class='zmdi zmdi-memory'></i><a href={os.environ.get('SERVER_ADDRESS')}ecosystem/apps/{repo_name}?id={app_id}>{app_name}</a>"

        # wont use
        # app_is_private = app["isPrivate"]
        # app_categories = app["config"].get("categories")
        # repo_name = app["slug"].split("/")[-1]
        # app_gh_url = f"<a href={app['repo']}>Link</a>"
        # ----
        # if app["config"].get("gpu") == "required" or app["config"].get("need_gpu") == True:
        # gpu_icon = "<i class='zmdi zmdi-memory'></i>"

        lines.append(
            [
                app_id,
                app_name_with_link,
                # app_description,
                Table.create_button(SELECT_APP),
            ]
        )
    df = pd.DataFrame(lines, columns=columns)
    table.read_pandas(df)


def create_app_selector_widgets():
    # SIDEBAR
    ecosystem_apps = g.api.app.get_list(g.TEAM_ID)  # -> AppsInfo
    # ecosystem_apps = g.api.app.get_list_ecosystem_modules(g.TEAM_ID) # -> dict

    serving_apps = [
        app
        for app in ecosystem_apps
        if app.name.lower().startswith("serve")
        and "serve" in app.config["categories"]
        and "interactive segmentation" not in app.config["categories"]
        and "salient object segmentation" not in app.config["categories"]
    ]
    app_selector_sidebar_table = Table(
        fixed_cols=len(columns), per_page=100, width="auto", sort_column_id=0, sort_direction="asc"
    )
    fill_apps_table(app_selector_sidebar_table, columns, serving_apps)

    app_selector_sidebar_field = Field(
        title="Select Serving App",
        description="Select serving app that you want to apply on your data.",
        content=app_selector_sidebar_table,
    )

    app_selector_sidebar_selected_app = Text("Selected app:", status="text")
    app_selector_sidebar_selected_app.hide()

    app_selector_sidebar_save_btn = create_save_btn()
    app_selector_sidebar_container = Container(
        [
            app_selector_sidebar_field,
            app_selector_sidebar_selected_app,
            app_selector_sidebar_save_btn,
        ]
    )
    # ------------------------------

    # PREVIEW
    # TODO: App thumbnail widget
    app_selector_preview = Text("Selected app:", status="text", font_size=get_text_font_size())
    # ------------------------------

    # LAYOUT
    app_selector_layout_edit_text = Text(
        "Select serving app", status="text", font_size=get_text_font_size()
    )
    app_selector_layout_edit_btn = Button(
        text="EDIT",
        icon="zmdi zmdi-edit",
        button_type="text",
        button_size="small",
        emit_on_click="openSidebar",
        style=get_set_settings_button_style(),
    )

    app_selector_layout_container = get_set_settings_container(
        app_selector_layout_edit_text, app_selector_layout_edit_btn
    )
    # ------------------------------

    return (
        # sidebar
        app_selector_sidebar_table,
        app_selector_sidebar_field,
        app_selector_sidebar_selected_app,
        app_selector_sidebar_save_btn,
        app_selector_sidebar_container,
        # preview
        app_selector_preview,
        # layout
        app_selector_layout_container,
    )
