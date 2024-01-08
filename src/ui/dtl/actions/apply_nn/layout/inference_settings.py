from supervisely.app.widgets import (
    Button,
    Container,
    Flexbox,
    Text,
    Field,
    Editor,
    Select,
    Input,
    Checkbox,
)
from src.ui.dtl.utils import (
    get_set_settings_button_style,
    get_set_settings_container,
    create_save_btn,
    create_set_default_btn,
    get_text_font_size,
)


def create_inference_settings_widgets():
    ### SIDEBAR LAYOUT
    model_suffix_input = Input(value="model", size="small")
    model_suffix_field = Field(
        title="Class / Tag name suffix",
        description="Add suffix to model class / tag name, if it has conflicts with existing one",
        content=model_suffix_input,
    )

    always_add_suffix_checkbox = Checkbox(
        content=Text("<b>Always add suffix to model predictions</b>", "text")
    )

    resolve_conflict_methods = [
        Select.Item(value="merge", label="Merge"),
        Select.Item(value="replace", label="Replace"),
    ]
    resolve_conflict_method_selector = Select(resolve_conflict_methods, size="small")
    resolve_conflict_method_field = Field(
        title="How to add predictions",
        description="Select how to add prediction to existing image annotation",
        content=resolve_conflict_method_selector,
    )

    inf_settings_editor = Editor(
        initial_text="Connect to model first",
        language_mode="yaml",
        restore_default_button=False,
        readonly=True,
    )
    inf_settings_editor_field = Field(
        title="Settings",
        description="Model specific inference settings in YAML format",
        content=inf_settings_editor,
    )

    inf_settings_save_btn = create_save_btn()
    inf_settings_set_default_btn = create_set_default_btn()

    apply_nn_selector_methods = [
        Select.Item("image", "Full Image"),
        Select.Item("roi", "ROI defined by object BBox (Coming Soon)", disabled=True),
        Select.Item("sliding_window", "Sliding Window (Coming Soon)", disabled=True),
    ]

    apply_nn_method_text = Text("Apply Method", font_size=get_text_font_size())
    apply_nn_methods_selector = Select(items=apply_nn_selector_methods, size="small")
    apply_nn_methods_field = Field(
        title="Apply Method",
        description="Select how you want to apply the model: to the images, to the ROI defined by object BBox or by using sliding window approach",
        content=apply_nn_methods_selector,
    )

    inf_settings_widgets_container = Container(
        widgets=[
            model_suffix_field,
            always_add_suffix_checkbox,
            resolve_conflict_method_field,
            inf_settings_editor_field,
            apply_nn_methods_field,
            Flexbox(
                widgets=[
                    inf_settings_save_btn,
                    inf_settings_set_default_btn,
                ],
                gap=110,
            ),
        ]
    )

    ### ------------------------------------------------------

    ### PREVIEW LAYOUT
    suffix_preview = Text("Suffix: ", "text", font_size=get_text_font_size())
    use_suffix_preview = Text("Always use suffix: ", "text", font_size=get_text_font_size())
    conflict_method_preview = Text(
        "How to add predictions: ", "text", font_size=get_text_font_size()
    )
    apply_method_preview = Text("Apply method: ", "text", font_size=get_text_font_size())

    suffix_preview.hide()
    use_suffix_preview.hide()
    conflict_method_preview.hide()
    apply_method_preview.hide()

    inf_settings_preview_container = Container(
        [
            suffix_preview,
            use_suffix_preview,
            conflict_method_preview,
            apply_method_preview,
        ]
    )

    ### ------------------------------------------------------

    ### NODE LAYOUT
    inf_settings_edit_text = Text("Inference Settings", "text", font_size=get_text_font_size())
    inf_settings_edit_btn = Button(
        text="EDIT",
        icon="zmdi zmdi-edit",
        button_type="text",
        button_size="small",
        emit_on_click="openSidebar",
        style=get_set_settings_button_style(),
    )
    inf_settings_edit_container = get_set_settings_container(
        inf_settings_edit_text, inf_settings_edit_btn
    )
    inf_settings_edit_container.hide()
    ### ------------------------------------------------------

    return (
        model_suffix_input,
        always_add_suffix_checkbox,
        resolve_conflict_method_selector,
        inf_settings_editor,
        apply_nn_methods_selector,
        inf_settings_save_btn,
        inf_settings_set_default_btn,
        suffix_preview,
        use_suffix_preview,
        conflict_method_preview,
        apply_method_preview,
        inf_settings_edit_text,
        inf_settings_edit_container,
        inf_settings_widgets_container,
        inf_settings_preview_container,
    )
