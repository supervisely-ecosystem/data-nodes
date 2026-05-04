import copy
from typing import Optional
from os.path import realpath, dirname

from supervisely import AnyGeometry, Bitmap, ProjectMeta
from supervisely.app.widgets import (
    Button,
    Container,
    Field,
    Flexbox,
    InputNumber,
    NodesFlow,
    Select,
    Text,
)

from src.ui.dtl.Action import AnnotationAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl.utils import (
    classes_list_settings_changed_meta,
    create_save_btn,
    create_set_default_btn,
    get_classes_list_value,
    get_layer_docs,
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
    set_classes_list_preview,
    set_classes_list_settings_from_json,
)
from src.ui.widgets import ClassesList, ClassesListPreview
import src.globals as g


class MaskMorphologyAction(AnnotationAction):
    name = "mask_morphology"
    title = "Mask Morphology"
    docs_url = (
        "https://docs.supervisely.com/data-manipulation/index/transformation-layers/"
        "mask_morphology"
    )
    description = "Applies mathematical morphology operations to bitmap masks."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None) -> Layer:
        _current_meta = ProjectMeta()
        classes_list_widget = ClassesList(multiple=True)
        classes_list_preview = ClassesListPreview()
        classes_list_save_btn = create_save_btn()
        classes_list_set_default_btn = create_set_default_btn()
        classes_list_widget_field = Field(
            content=classes_list_widget,
            title="Classes",
            description="Select BITMAP classes whose masks will be processed",
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
        classes_list_edit_text = Text("Classes", status="text", font_size=get_text_font_size())
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

        operation_text = Text("Operation", status="text", font_size=get_text_font_size())
        operation_selector = Select(
            [
                Select.Item("open", "Open"),
                Select.Item("close", "Close"),
                Select.Item("erode", "Erode"),
                Select.Item("dilate", "Dilate"),
            ],
            size="small",
        )
        kernel_shape_text = Text("Kernel shape", status="text", font_size=get_text_font_size())
        kernel_shape_selector = Select(
            [
                Select.Item("ellipse", "Ellipse"),
                Select.Item("rectangle", "Rectangle"),
                Select.Item("cross", "Cross"),
            ],
            size="small",
        )
        kernel_size_text = Text("Kernel size", status="text", font_size=get_text_font_size())
        kernel_size_input = InputNumber(value=3, min=1, step=2, controls=True, size="small")
        iterations_text = Text("Iterations", status="text", font_size=get_text_font_size())
        iterations_input = InputNumber(value=1, min=1, step=1, controls=True, size="small")

        saved_classes_settings = "default"
        default_classes_settings = "default"

        def _get_classes_list_value():
            return get_classes_list_value(classes_list_widget, multiple=True)

        def _set_classes_list_preview():
            set_classes_list_preview(
                classes_list_widget,
                classes_list_preview,
                saved_classes_settings,
                classes_list_edit_text,
            )

        def _save_classes_list_settings():
            nonlocal saved_classes_settings
            saved_classes_settings = _get_classes_list_value()

        def _set_default_classes_mapping_setting():
            nonlocal saved_classes_settings
            saved_classes_settings = copy.deepcopy(default_classes_settings)

        def data_changed_cb(**kwargs):
            project_meta = kwargs.get("project_meta", None)
            if project_meta is None:
                return
            nonlocal _current_meta
            if project_meta == _current_meta:
                return
            _current_meta = project_meta

            classes_list_widget.loading = True
            obj_classes = [
                cls
                for cls in project_meta.obj_classes
                if cls.geometry_type in [Bitmap, AnyGeometry]
            ]
            classes_list_widget.set(obj_classes)

            nonlocal saved_classes_settings
            saved_classes_settings = classes_list_settings_changed_meta(
                saved_classes_settings, obj_classes
            )

            classes_names = saved_classes_settings
            if classes_names == "default":
                classes_names = [cls.name for cls in obj_classes]
            classes_list_widget.select(classes_names)

            _set_classes_list_preview()
            classes_list_widget.loading = False

        def get_settings(options_json: dict) -> dict:
            classes = saved_classes_settings
            if saved_classes_settings == "default":
                classes = _get_classes_list_value()
            return {
                "classes": classes,
                "operation": operation_selector.get_value(),
                "kernel_shape": kernel_shape_selector.get_value(),
                "kernel_size": kernel_size_input.get_value(),
                "iterations": iterations_input.get_value(),
            }

        def _set_settings_from_json(settings: dict):
            classes_list_widget.loading = True
            classes_list_settings = settings.get("classes", default_classes_settings)
            set_classes_list_settings_from_json(
                classes_list_widget=classes_list_widget, settings=classes_list_settings
            )
            if classes_list_settings != "default":
                _save_classes_list_settings()
            _set_classes_list_preview()
            classes_list_widget.loading = False

            operation_selector.set_value(settings.get("operation", "open"))
            kernel_shape_selector.set_value(settings.get("kernel_shape", "ellipse"))
            kernel_size_input.value = settings.get("kernel_size", 3)
            iterations_input.value = settings.get("iterations", 1)

        @classes_list_save_btn.click
        def classes_list_save_btn_cb():
            _save_classes_list_settings()
            _set_classes_list_preview()
            g.updater("metas")

        @classes_list_set_default_btn.click
        def classes_list_set_default_btn_cb():
            _set_default_classes_mapping_setting()
            set_classes_list_settings_from_json(
                classes_list_widget=classes_list_widget, settings=saved_classes_settings
            )
            _set_classes_list_preview()
            g.updater("metas")

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="Select Classes",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=classes_list_edit_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(
                            classes_list_widgets_container
                        ),
                        sidebar_width=380,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="classes_preview_text",
                    option_component=NodesFlow.WidgetOptionComponent(classes_list_preview),
                ),
                NodesFlow.Node.Option(
                    name="operation_text",
                    option_component=NodesFlow.WidgetOptionComponent(operation_text),
                ),
                NodesFlow.Node.Option(
                    name="operation_selector",
                    option_component=NodesFlow.WidgetOptionComponent(operation_selector),
                ),
                NodesFlow.Node.Option(
                    name="kernel_shape_text",
                    option_component=NodesFlow.WidgetOptionComponent(kernel_shape_text),
                ),
                NodesFlow.Node.Option(
                    name="kernel_shape_selector",
                    option_component=NodesFlow.WidgetOptionComponent(kernel_shape_selector),
                ),
                NodesFlow.Node.Option(
                    name="kernel_size_text",
                    option_component=NodesFlow.WidgetOptionComponent(kernel_size_text),
                ),
                NodesFlow.Node.Option(
                    name="kernel_size_input",
                    option_component=NodesFlow.WidgetOptionComponent(kernel_size_input),
                ),
                NodesFlow.Node.Option(
                    name="iterations_text",
                    option_component=NodesFlow.WidgetOptionComponent(iterations_text),
                ),
                NodesFlow.Node.Option(
                    name="iterations_input",
                    option_component=NodesFlow.WidgetOptionComponent(iterations_input),
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
            data_changed_cb=data_changed_cb,
        )
