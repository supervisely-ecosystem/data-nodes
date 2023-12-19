import os
from typing import Optional, List
from os.path import realpath, dirname
from supervisely.app.widgets import (
    NodesFlow,
    Input,
    Text,
    Select,
    Table,
    Button,
    Container,
    Field,
    Empty,
)
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


def create_app_serve_widgets():
    # LAYOUT
    app_serve_layout_edit_text = Empty()
    app_serve_layout_button = Button(
        text="SERVE",
        icon="zmdi zmdi-play",
        button_type="text",
        button_size="small",
        style=get_set_settings_button_style(),
    )

    app_serve_layout_container = get_set_settings_container(
        app_serve_layout_edit_text, app_serve_layout_button
    )
    # ----------------------
    return (
        # layout
        app_serve_layout_button,
        app_serve_layout_container,
    )
