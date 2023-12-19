from typing import Optional
from os.path import realpath, dirname
from supervisely.app.widgets import NodesFlow, Input, Text, Select, Table

from src.ui.dtl import NeuralNetworkAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import get_layer_docs, get_text_font_size
import src.globals as g


from src.ui.dtl.actions.serve_nn.layout.app_selector import create_app_selector_widgets
from src.ui.dtl.actions.serve_nn.layout.agent_selector import create_agent_selector_widgets
from src.ui.dtl.actions.serve_nn.layout.app_serve import create_app_serve_widgets


class ServeNNAction(NeuralNetworkAction):
    name = "serve_nn"
    title = "Serve NN"
    docs_url = None
    description = "Select and serve NN model."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        saved_settings = {}

        # APP SELECTOR
        (  # sidebar
            app_selector_sidebar_table,
            app_selector_sidebar_field,
            app_selector_sidebar_selected_app,
            app_selector_sidebar_save_btn,
            app_selector_sidebar_container,
            # preview
            app_selector_preview,
            # layout
            app_selector_layout_container,
        ) = create_app_selector_widgets()

        # APP SELECTOR CBs
        @app_selector_sidebar_table.click
        def app_selector_sidebar_table_click(data: Table.ClickedDataPoint):
            pass

        @app_selector_sidebar_save_btn.click
        def app_selector_sidebar_save_btn_click():
            pass

        # ----------------------

        # AGENT SELECTOR
        (  # sidebar
            agent_selector_sidebar_table,
            agent_selector_sidebar_field,
            agent_selector_sidebar_save_btn,
            agent_selector_sidebar_container,
            # preview
            agent_selector_preview,
            # layout
            agent_selector_layout_container,
        ) = create_agent_selector_widgets()
        # AGENT SELECTOR CBs

        @agent_selector_sidebar_table.click
        def agent_selector_sidebar_table_click(data: Table.ClickedDataPoint):
            pass

        @agent_selector_sidebar_save_btn.click
        def agent_selector_sidebar_save_btn_click():
            pass

        # ----------------------

        # APP SERVE
        (  # layout
            app_serve_layout_button,
            app_serve_layout_container,
        ) = create_app_serve_widgets()

        # APP LAUNCH CBs
        @app_serve_layout_button.click
        def app_serve_layout_button_click():
            pass

        # ----------------------

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return {}

        def _set_settings_from_json(settings: dict):
            pass

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="App selector",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=app_selector_layout_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(
                            app_selector_sidebar_container
                        ),
                        sidebar_width=460,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="App selector preview",
                    option_component=NodesFlow.WidgetOptionComponent(app_selector_preview),
                ),
                NodesFlow.Node.Option(
                    name="Agent selector",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=agent_selector_layout_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(
                            agent_selector_sidebar_container
                        ),
                        sidebar_width=420,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="Agent selector preview",
                    option_component=NodesFlow.WidgetOptionComponent(agent_selector_preview),
                ),
                NodesFlow.Node.Option(
                    name="App serve",
                    option_component=NodesFlow.WidgetOptionComponent(app_serve_layout_container),
                ),
            ]
            return {
                "src": [],
                "dst": [],
                "settings": settings_options,
            }

        return Layer(
            action=cls,
            id=layer_id,
            create_options=create_options,
            get_settings=get_settings,
            need_preview=False,
        )
