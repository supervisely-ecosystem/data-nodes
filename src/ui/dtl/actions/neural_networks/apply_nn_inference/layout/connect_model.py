from supervisely.app.widgets import (
    Button,
    Container,
    Text,
    Field,
    Flexbox,
    ModelInfo,
    SelectAppSession,
)
from src.ui.dtl.utils import (
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
    create_sidebar_btn_container,
)
import src.globals as g

SESSION_TAGS = [
    "deployed_nn",
    # "deployed_nn_cls",
    # "deployed_nn_3d",
    # "sly_video_tracking",
    # "sly_smart_annotation",
    # "deployed_nn_embeddings",
    # "sly_point_cloud_tracking",
    # "deployed_nn_recommendations",
    # "labeling_jobs",
    # "sly_interpolation",
]


def create_connect_to_model_widgets() -> tuple:
    connect_nn_text = Text("Connect to Model", "text", font_size=get_text_font_size())
    connect_nn_model_preview = Text("No model selected", "text", font_size=get_text_font_size())
    connect_nn_model_preview.hide()

    connect_nn_edit_btn = Button(
        text="CONNECT",
        icon="zmdi zmdi-router",
        button_type="text",
        button_size="small",
        emit_on_click="openSidebar",
        style=get_set_settings_button_style(),
    )
    connect_nn_edit_container = get_set_settings_container(connect_nn_text, connect_nn_edit_btn)
    connect_nn_connect_btn = Button(
        "Connect", icon="zmdi zmdi-play", call_on_click="closeSidebar();"
    )
    connect_nn_connect_btn.disable()
    connect_nn_disconnect_btn = Button(
        "Disconnect",
        button_type="info",
        plain=True,
        icon="zmdi zmdi-stop",
        # call_on_click="closeSidebar();",
    )
    connect_nn_disconnect_btn.disable()

    connect_nn_model_selector = SelectAppSession(team_id=g.TEAM_ID, tags=SESSION_TAGS)
    connect_nn_model_selector_disabled_text = Text(
        "Deploy node has been detected. Unplug deploy node if you want to manually select model",
        "info",
    )
    connect_nn_model_selector_disabled_text.hide()

    connect_nn_model_field = Field(
        title="Select deployed model",
        description="Connect deploy node or deploy model manually via one of the serving apps and then choose it in selector",
        content=connect_nn_model_selector,
    )

    connect_nn_model_info = ModelInfo()
    connect_nn_model_info_empty_text = Text("Select model first", "info")
    connect_nn_model_info_container = Container(
        [connect_nn_model_info, connect_nn_model_info_empty_text], gap=0
    )
    connect_nn_model_info_field = Field(
        title="Model Info",
        description="Technical details and configurations for deployed model",
        content=connect_nn_model_info_container,
    )
    connect_nn_widgets_container = Container(
        widgets=[
            connect_nn_model_field,
            connect_nn_model_selector_disabled_text,
            connect_nn_model_info_field,
            create_sidebar_btn_container(connect_nn_connect_btn, connect_nn_disconnect_btn, True),
        ]
    )
    model_separator = Text("<hr>")
    model_separator.hide()
    return (
        connect_nn_text,
        connect_nn_model_preview,
        connect_nn_edit_btn,
        connect_nn_edit_container,
        connect_nn_connect_btn,
        connect_nn_disconnect_btn,
        connect_nn_model_selector,
        connect_nn_model_field,
        connect_nn_model_selector_disabled_text,
        connect_nn_model_info,
        connect_nn_model_info_empty_text,
        connect_nn_model_info_container,
        connect_nn_model_info_field,
        connect_nn_widgets_container,
        model_separator,
    )
