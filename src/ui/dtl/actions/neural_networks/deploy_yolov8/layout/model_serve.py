from supervisely.app.widgets import Text, Button, NotificationBox

from src.ui.dtl.utils import (
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
)


def create_model_serve_widgets():
    model_serve_preview = Text("Action required", "text", font_size=get_text_font_size())
    model_serve_btn = Button(
        text="SERVE",
        icon="zmdi zmdi-play",
        button_type="text",
        button_size="small",
        style="flex: auto; border: 1px solid #bfcbd9; color: white; background-color: #409eff;",
    )
    model_serve_layout_container = get_set_settings_container(model_serve_preview, model_serve_btn)
    model_serve_postprocess_message = NotificationBox(
        title="App session has been shutdown",
        description="Model has been automatically stopped. Press SERVE button to deploy another model and continue",
        box_type="info",
    )
    model_serve_postprocess_message.hide()
    return (
        model_serve_preview,
        model_serve_btn,
        model_serve_layout_container,
        model_serve_postprocess_message,
    )
