from supervisely.app.widgets import (
    Button,
    Container,
    Flexbox,
    Text,
    Field,
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


def create_job_settings_classes_widgets() -> tuple:
    lj_settings_classes_list_widget_notification = NotificationBox(
        title="No classes",
        description="Make sure that you have selected input project that has classes",
    )
    lj_settings_classes_list_widget = ClassesList(
        multiple=True, empty_notification=lj_settings_classes_list_widget_notification
    )
    lj_settings_classes_list_preview = ClassesListPreview(empty_text="No classes selected")
    # lj_settings_classes_list_preview.hide()

    lj_settings_classes_list_save_btn = create_save_btn()
    lj_settings_classes_list_set_default_btn = create_set_default_btn()

    lj_settings_classes_list_widget_field = Field(
        content=lj_settings_classes_list_widget,
        title="Classes",
        description="Select classes that will be used by annotators",
    )
    lj_settings_classes_list_widgets_container = Container(
        widgets=[
            lj_settings_classes_list_widget_field,
            Flexbox(
                widgets=[
                    lj_settings_classes_list_save_btn,
                    lj_settings_classes_list_set_default_btn,
                ],
                gap=110,
            ),
        ]
    )

    lj_settings_classes_list_edit_text = Text(
        "Classes: 0 / 0", status="text", font_size=get_text_font_size()
    )
    lj_settings_classes_list_edit_btn = Button(
        text="EDIT",
        icon="zmdi zmdi-edit",
        button_type="text",
        button_size="small",
        emit_on_click="openSidebar",
        style=get_set_settings_button_style(),
    )
    lj_settings_classes_list_edit_container = get_set_settings_container(
        lj_settings_classes_list_edit_text, lj_settings_classes_list_edit_btn
    )
    # lj_settings_classes_list_edit_container.hide()
    return (
        # sidebar
        lj_settings_classes_list_widget,
        lj_settings_classes_list_save_btn,
        lj_settings_classes_list_set_default_btn,
        lj_settings_classes_list_widgets_container,
        # preview
        lj_settings_classes_list_preview,
        # layout
        lj_settings_classes_list_edit_text,
        lj_settings_classes_list_edit_btn,
        lj_settings_classes_list_edit_container,
    )
