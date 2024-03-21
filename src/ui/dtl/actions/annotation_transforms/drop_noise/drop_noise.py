import copy
from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import (
    NodesFlow,
    Switch,
    InputNumber,
    OneOf,
    Flexbox,
    Button,
    Container,
    Text,
    Select,
    Field,
)
from supervisely import ProjectMeta, Bitmap, AnyGeometry

from src.ui.dtl import AnnotationAction
from src.ui.dtl.Layer import Layer
from src.ui.widgets import ClassesList, ClassesListPreview
from src.ui.dtl.utils import (
    classes_list_settings_changed_meta,
    get_classes_list_value,
    set_classes_list_preview,
    set_classes_list_settings_from_json,
    get_set_settings_button_style,
    get_set_settings_container,
    get_layer_docs,
    create_save_btn,
    create_set_default_btn,
    get_text_font_size,
)
import src.globals as g


class DropNoiseAction(AnnotationAction):
    name = "drop_noise"
    title = "Drop Noise"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/transformation-layers/drop_noise_from_bitmap"
    description = (
        "Removes connected components smaller than the specified size from bitmap annotations."
    )
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        _current_meta = ProjectMeta()
        classes_list_widget = ClassesList(multiple=True)
        classes_list_preview = ClassesListPreview()
        save_classes_btn = create_save_btn()
        set_default_classes_btn = create_set_default_btn()
        classes_list_widget_field = Field(
            content=classes_list_widget,
            title="Classes",
            description="Select BITMAP classes for whose masks noise in the form of components smaller than the specified size will be removed",
        )
        classes_list_widgets_container = Container(
            widgets=[
                classes_list_widget_field,
                Flexbox(
                    widgets=[
                        save_classes_btn,
                        set_default_classes_btn,
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
            # save setting to var
            nonlocal saved_classes_settings
            saved_classes_settings = copy.deepcopy(default_classes_settings)

        min_area_text = Text("Min Area", status="text", font_size=get_text_font_size())
        measure_unit_selector = Select(
            [Select.Item("px", "pixels"), Select.Item("%", "percents")],
            size="small",
        )
        min_area_input = InputNumber(value=1024, min=1, step=1, size="small", controls=True)

        @measure_unit_selector.value_changed
        def measure_unit_selector_cb(value):
            if value == "%":
                if min_area_input.get_value() > 100:
                    min_area_input.value = 100

        @min_area_input.value_changed
        def min_area_input_cb(value):
            if measure_unit_selector.get_value() == "%":
                if min_area_input.get_value() > 100:
                    min_area_input.value = 100

        min_area_widgets = Flexbox(widgets=[measure_unit_selector, min_area_input])

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            classes = saved_classes_settings
            if saved_classes_settings == "default":
                classes = _get_classes_list_value()
            return {
                "classes": classes,
                "min_area": _get_min_area(),
                "src_type": source_type_selector.get_value(),
            }

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

            # set classes to widget
            classes_list_widget.set(obj_classes)

            # update settings according to new meta
            nonlocal saved_classes_settings
            saved_classes_settings = classes_list_settings_changed_meta(
                saved_classes_settings, obj_classes
            )

            classes_names = saved_classes_settings
            if classes_names == "default":
                classes_names = [cls.name for cls in obj_classes]
            classes_list_widget.select(classes_names)

            # update settings preview
            _set_classes_list_preview()

            classes_list_widget.loading = False

        def _get_min_area():
            return f"{min_area_input.get_value()}{measure_unit_selector.get_value()}"

        def _set_settings_from_json(settings: dict):
            classes_list_widget.loading = True
            classes_list_settings = settings.get("classes", default_classes_settings)
            set_classes_list_settings_from_json(
                classes_list_widget=classes_list_widget, settings=classes_list_settings
            )
            # save settings
            if classes_list_settings != "default":
                _save_classes_list_settings()
            # update settings preview
            _set_classes_list_preview()
            classes_list_widget.loading = False

            min_area = settings.get("min_area", None)
            if min_area is not None:
                if min_area[-1] == "%":
                    min_area_input.value = int(min_area[:-1])
                    measure_unit_selector.set_value("%")
                else:
                    min_area_input.value = int(min_area[:-2])
                    measure_unit_selector.set_value("px")

            source_type = settings.get("src_type", None)
            if source_type is not None:
                source_type_selector.set_value(source_type)

        source_type_text = Text("Source type", status="text", font_size=get_text_font_size())
        source_type_selector = Select(
            [Select.Item("image", "Image"), Select.Item("bbox", "Bounding Box")],
            size="small",
        )

        @save_classes_btn.click
        def classes_list_save_btn_cb():
            _save_classes_list_settings()
            _set_classes_list_preview()
            g.updater("metas")

        @set_default_classes_btn.click
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
                    name="Min Area",
                    option_component=NodesFlow.WidgetOptionComponent(min_area_text),
                ),
                NodesFlow.Node.Option(
                    name="min_area_widgets",
                    option_component=NodesFlow.WidgetOptionComponent(min_area_widgets),
                ),
                NodesFlow.Node.Option(
                    name="source_type_text",
                    option_component=NodesFlow.WidgetOptionComponent(source_type_text),
                ),
                NodesFlow.Node.Option(
                    name="source_type_selector",
                    option_component=NodesFlow.WidgetOptionComponent(source_type_selector),
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
