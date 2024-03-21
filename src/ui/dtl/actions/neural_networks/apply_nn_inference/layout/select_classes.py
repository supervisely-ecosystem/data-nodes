from supervisely.app.widgets import (
    Button,
    Container,
    Flexbox,
    Text,
    Field,
    MatchObjClasses,
    NotificationBox,
)
from src.ui.widgets import ClassesList, ClassesListPreview
from src.ui.dtl.utils import (
    get_set_settings_button_style,
    get_set_settings_container,
    create_save_btn,
    create_set_default_btn,
    get_text_font_size,
)


def create_classes_selector_widgets() -> tuple:
    # match_obj_classes_widget = MatchObjClasses()
    # match_obj_classes_widget.hide()

    classes_list_widget_notification = NotificationBox(
        title="No classes",
        description="Connect to deployed model to display classes.",
    )
    classes_list_widget = ClassesList(
        multiple=True, empty_notification=classes_list_widget_notification
    )
    classes_list_preview = ClassesListPreview(empty_text="No classes selected")
    classes_list_preview.hide()

    classes_list_save_btn = create_save_btn()
    classes_list_set_default_btn = create_set_default_btn()

    classes_list_widget_field = Field(
        content=classes_list_widget,
        title="Model Classes",
        description="Select classes from model",
    )
    classes_list_widgets_container = Container(
        widgets=[
            classes_list_widget_field,
            Flexbox(
                widgets=[
                    classes_list_save_btn,
                    classes_list_set_default_btn,
                ],
                gap=110,
            ),
        ]
    )

    classes_list_edit_text = Text("Model Classes", status="text", font_size=get_text_font_size())
    classes_list_edit_btn = Button(
        text="EDIT",
        icon="zmdi zmdi-edit",
        button_type="text",
        button_size="small",
        emit_on_click="openSidebar",
        style=get_set_settings_button_style(),
    )
    classes_list_edit_container = get_set_settings_container(
        classes_list_edit_text, classes_list_edit_btn
    )
    classes_list_edit_container.hide()
    classes_separator = Text("<hr>")
    classes_separator.hide()
    return (
        classes_list_widget_notification,
        classes_list_widget,
        classes_list_preview,
        classes_list_save_btn,
        classes_list_set_default_btn,
        classes_list_widget_field,
        classes_list_widgets_container,
        classes_list_edit_text,
        classes_list_edit_btn,
        classes_list_edit_container,
        classes_separator,
    )
