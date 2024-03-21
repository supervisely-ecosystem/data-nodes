from typing import Optional
from os.path import realpath, dirname

from supervisely.app.widgets import (
    NodesFlow,
    Select,
    InputNumber,
    SelectTagMeta,
    Container,
    Field,
    Input,
    OneOf,
    Button,
    Text,
    Field,
)
from supervisely import ProjectMeta

from src.ui.dtl import FilterAndConditionAction
from src.ui.dtl.Layer import Layer
from src.ui.widgets import ClassesList, ClassesListPreview, TagsList, TagsListPreview
from src.ui.dtl.utils import (
    get_set_settings_button_style,
    get_set_settings_container,
    get_layer_docs,
    create_save_btn,
    get_text_font_size,
    set_tags_list_preview,
    get_tags_list_value,
)


class IfAction(FilterAndConditionAction):
    name = "if"
    title = "If"
    docs_url = "https://docs.supervisely.com/data-manipulation/index/transformation-layers/if"
    description = "Split input data to several flows with a specified criterion."
    md_description = get_layer_docs(dirname(realpath(__file__)))

    @classmethod
    def create_new_layer(cls, layer_id: Optional[str] = None):
        class Condition:
            def __init__(
                self, name, title, widget, get_func, set_func, preview_widget, set_preview_func
            ):
                self.name = name
                self.title = title
                self.widget = widget
                self.get_func = get_func
                self.set_func = set_func
                self.preview_widget = preview_widget
                self.set_preview_func = set_preview_func

            def item(self):
                return Select.Item(self.name, self.title, self.widget)

            def get(self):
                return self.get_func()

            def set(self, value):
                self.set_func(value)
                select_condition.set_value(self.name)

            def preview_item(self):
                return Select.Item(self.name, self.title, self.preview_widget)

            def set_preview(self):
                self.set_preview_func()

        _current_meta = ProjectMeta()

        # probability
        _prob_input = InputNumber(value=20, min=0, max=100, precision=3)
        _probability_condition_widget = Field(
            title="Probability",
            description="Set probability percentage to split data",
            content=_prob_input,
        )

        def _get_prob_value():
            return _prob_input.get_value() / 100

        def _set_prob_value(condition_json):
            _prob_input.value = condition_json["probability"] * 100

        _prob_preview_widget = Text("", status="text", font_size=get_text_font_size())

        def _set_prob_preview():
            _prob_preview_widget.text = f"Probability: {_get_prob_value()}"

        probability_condition = Condition(
            name="probability",
            title="Probability",
            widget=_probability_condition_widget,
            get_func=_get_prob_value,
            set_func=_set_prob_value,
            preview_widget=_prob_preview_widget,
            set_preview_func=_set_prob_preview,
        )

        # min objects count
        _min_objects_count_input = InputNumber(min=0, max=None)
        _min_objects_count_condition_widget = Field(
            title="Min objects count",
            description="Set minimum objects count on the image to split data. Images with objects count less than specified will be sent to the 'False' output",
            content=_min_objects_count_input,
        )

        def _set_min_obj_count_value(condition_json):
            _min_objects_count_input.value = condition_json["min_objects_count"]

        _min_objects_preview_widget = Text("", status="text", font_size=get_text_font_size())

        def _set_min_obj_preview():
            _min_objects_preview_widget.text = (
                f"Min objects count: {_min_objects_count_input.get_value()}"
            )

        min_objects_count_condition = Condition(
            name="min_objects_count",
            title="Min objects count",
            widget=_min_objects_count_condition_widget,
            get_func=_min_objects_count_input.get_value,
            set_func=_set_min_obj_count_value,
            preview_widget=_min_objects_preview_widget,
            set_preview_func=_set_min_obj_preview,
        )

        # min height
        _min_height_input = InputNumber(min=0, max=None)
        _min_height_condition_widget = Field(
            title="Min height",
            description="Set minimum image height to split data. Images with height less than specified will be sent to the 'False' output",
            content=_min_height_input,
        )

        def _set_min_height_value(condition_json):
            _min_height_input.value = condition_json["min_height"]

        _min_height_preview_widget = Text("", status="text", font_size=get_text_font_size())

        def _min_height_preview():
            _min_height_preview_widget.text = f"Min height: {_min_height_input.get_value()}"

        min_height_condition = Condition(
            name="min_height",
            title="Min height",
            widget=_min_height_condition_widget,
            get_func=_min_height_input.get_value,
            set_func=_set_min_height_value,
            preview_widget=_min_height_preview_widget,
            set_preview_func=_min_height_preview,
        )

        # tags
        _select_tags_input = TagsList(multiple=True)

        _select_tags_widget = Field(
            title="Include Tags",
            description="Select one or more tags that are assigned to image to split data. Images with selected tags will be sent to the 'True' output, others to the 'False' output",
            content=_select_tags_input,
        )

        def _set_tags_value(condition_json):
            # _select_tags_input.set_names(condition_json["tags"])
            nonlocal _current_meta
            selected_tags = condition_json["tags"]
            _select_tags_input.set(_current_meta.tag_metas)
            _select_tags_input.select(selected_tags)

        _tags_preview_widget = TagsListPreview()

        def _set_tags_preview():
            nonlocal _current_meta
            tags_to_set = []
            selected_tags = _select_tags_input.get_selected_tags()
            selected_tags_names = [tag.name for tag in selected_tags]
            if _current_meta is not None:
                for tag in _current_meta.tag_metas:
                    if tag.name in selected_tags_names:
                        tags_to_set.append(tag)
            _tags_preview_widget.set(tags_to_set)

        def _get_tags_value():
            return get_tags_list_value(_select_tags_input, multiple=True)

        _include_tags_text = Text("Include Tags", status="text", font_size=get_text_font_size())
        select_tags_condition = Condition(
            name="tags",
            title="Tags",
            widget=_select_tags_widget,
            get_func=_get_tags_value,
            set_func=_set_tags_value,
            preview_widget=Container(
                widgets=[
                    _include_tags_text,
                    _tags_preview_widget,
                ],
                gap=1,
            ),
            set_preview_func=_set_tags_preview,
        )

        # include classes
        _include_classes_input = ClassesList(multiple=True)
        _include_classes_widget = Field(
            title="Include classes",
            description=(
                "Select one or more classes to split data. "
                "Images that have at least one object of the selected classes "
                "will go to the True output branch, "
                "other images will go to the 'False' output branch"
            ),
            content=_include_classes_input,
        )

        def _set_include_classes_value(condition_json):
            _include_classes_input.select(condition_json["include_classes"])

        _include_classes_preview_widget = ClassesListPreview()

        def _set_include_classes_preview():
            _include_classes_preview_widget.set(_include_classes_input.get_selected_classes())

        include_classes_text = Text(
            "Include Classes:", status="text", font_size=get_text_font_size()
        )
        select_classes_condition = Condition(
            name="include_classes",
            title="Include classes",
            widget=_include_classes_widget,
            get_func=lambda: [oc.name for oc in _include_classes_input.get_selected_classes()],
            set_func=_set_include_classes_value,
            preview_widget=Container(
                widgets=[
                    include_classes_text,
                    _include_classes_preview_widget,
                ],
                gap=1,
            ),
            set_preview_func=_set_include_classes_preview,
        )

        # name in range
        # _names_in_range_inputs = {
        #     "name_from": Input(size="small"),
        #     "name_to": Input(size="small"),
        #     "step": InputNumber(value=1, min=1, max=None),
        # }
        # _names_in_range_widget = Field(
        #     title="Name in range",
        #     description="Input name in range",
        #     content=Container(
        #         widgets=[
        #             Field(title="Name from", content=_names_in_range_inputs["name_from"]),
        #             Field(title="Name to", content=_names_in_range_inputs["name_to"]),
        #             Field(title="Step", content=_names_in_range_inputs["step"]),
        #         ]
        #     ),
        # )

        # def _set_names_in_range_value(condition_json):
        #     name_from, name_to = condition_json["name_in_range"]
        #     _names_in_range_inputs["name_from"].set_value(name_from)
        #     _names_in_range_inputs["name_to"].set_value(name_to)
        #     _names_in_range_inputs["step"].value = condition_json["name_in_range"]["frame_step"]

        # def _get_names_in_range_value():
        #     return {
        #         "name_in_range": [
        #             _names_in_range_inputs["name_from"].get_value(),
        #             _names_in_range_inputs["name_to"].get_value(),
        #         ],
        #         "frame_step": _names_in_range_inputs["step"].get_value(),
        #     }

        # _names_in_range_preview_range = Text("", status="text", font_size=get_text_font_size())
        # _names_in_range_preview_step = Text("", status="text", font_size=get_text_font_size())
        # _names_in_range_preview_widget = Container(
        #     widgets=[_names_in_range_preview_range, _names_in_range_preview_step], gap=1
        # )

        # def _set_names_in_range_preview():
        #     value = _get_names_in_range_value()
        #     _names_in_range_preview_range.text = (
        #         f"Name in range: from {value['name_in_range'][0]} to {value['name_in_range'][1]}"
        #     )
        #     _names_in_range_preview_step.text = f"Step: {value['frame_step']}"

        # names_in_range_condition = Condition(
        #     name="name_in_range",
        #     title="Name in range",
        #     widget=_names_in_range_widget,
        #     get_func=_get_names_in_range_value,
        #     set_func=_set_names_in_range_value,
        #     preview_widget=_names_in_range_preview_widget,
        #     set_preview_func=_set_names_in_range_preview,
        # )

        conditions = {
            condition.name: condition
            for condition in [
                probability_condition,
                min_objects_count_condition,
                min_height_condition,
                select_tags_condition,
                select_classes_condition,
                # names_in_range_condition,
            ]
        }

        select_condition_items = [condition.item() for condition in conditions.values()]
        select_condition = Select(items=select_condition_items, size="small")
        condition_input = OneOf(select_condition)

        preview_items = [condition.preview_item() for condition in conditions.values()]
        _select_preview = Select(
            items=preview_items,
            size="small",
        )
        settings_preview = OneOf(_select_preview)
        save_settings_btn = create_save_btn()
        settings_edit_text = Text("Condition", status="text", font_size=get_text_font_size())
        settings_edit_btn = Button(
            text="EDIT",
            icon="zmdi zmdi-edit",
            button_type="text",
            button_size="small",
            emit_on_click="openSidebar",
            style=get_set_settings_button_style(),
        )
        settings_edit_container = get_set_settings_container(settings_edit_text, settings_edit_btn)

        saved_settings = {}

        widget = Container(
            widgets=[
                Field(
                    title="Condition",
                    description="Select condition to filter data",
                    content=select_condition,
                ),
                Field(title="Condition settings", content=condition_input),
                save_settings_btn,
            ]
        )

        def _get_condition_value(condition_name: str):
            condition = conditions[condition_name]
            return condition.get()

        def _set_preview(condition_name: str):
            condition = conditions[condition_name]
            condition.set_preview()

        def _save_settings():
            nonlocal saved_settings
            condition_name = select_condition.get_value()
            condition_value = _get_condition_value(condition_name)
            saved_settings = {
                "condition": {condition_name: condition_value},
            }
            _set_preview(condition_name)
            _select_preview.set_value(condition_name)

        def get_settings(options_json: dict) -> dict:
            """This function is used to get settings from options json we get from NodesFlow widget"""
            return saved_settings

        def data_changed_cb(**kwargs):
            project_meta = kwargs.get("project_meta", None)
            if project_meta is None:
                return
            nonlocal _current_meta
            if project_meta == _current_meta:
                return
            _current_meta = project_meta
            _include_classes_input.loading = True
            _select_tags_input.loading = True
            _include_classes_input.set(project_meta.obj_classes)
            _select_tags_input.set(project_meta.tag_metas)
            _include_classes_input.loading = False
            _select_tags_input.loading = False

        def _set_settings_from_json(settings: dict):
            if not "condition" in settings:
                settings = {"condition": {"probability": 0.2}}

            condition_json = settings["condition"]
            condition_name, _ = list(settings["condition"].items())[0]
            condition = conditions[condition_name]
            condition.set(condition_json)
            _save_settings()

        save_settings_btn.click(_save_settings)

        def create_options(src: list, dst: list, settings: dict) -> dict:
            _set_settings_from_json(settings)
            settings_options = [
                NodesFlow.Node.Option(
                    name="Set Condition",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=settings_edit_container,
                        sidebar_component=NodesFlow.WidgetOptionComponent(widget),
                        sidebar_width=300,
                    ),
                ),
                NodesFlow.Node.Option(
                    name="Settings Preview",
                    option_component=NodesFlow.WidgetOptionComponent(settings_preview),
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
            need_preview=False,
        )

    @classmethod
    def create_outputs(cls):
        return [
            NodesFlow.Node.Output("destination_true", "Output True"),
            NodesFlow.Node.Output("destination_false", "Output False"),
        ]
