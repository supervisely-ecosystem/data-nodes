import os
import copy
import time
from typing import Optional, List
import random

from supervisely import Annotation, ProjectMeta
from supervisely.app.widgets import (
    ImageAnnotationPreview,
    NodesFlow,
    Markdown,
    Button,
    Text,
    Container,
)
from supervisely.imaging.image import write as write_image

from src.ui.dtl.Action import Action
from src.ui.dtl.utils import (
    get_separator,
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
)
import src.globals as g
from src.compute.dtl_utils.item_descriptor import ImageDescriptor


class Layer:
    def __init__(
        self,
        action: Action,
        create_options: callable,
        get_src: Optional[callable] = None,
        get_settings: Optional[callable] = None,
        get_dst: Optional[callable] = None,
        data_changed_cb: Optional[callable] = None,
        need_preview: bool = True,
        id: Optional[str] = None,
        custom_update_btn: Button = None,
        get_data: Optional[callable] = None,
        postprocess_cb: Optional[callable] = None,
        update_sources_cb: Optional[callable] = None,
    ):
        self.action = action
        self.id = id
        if self.id is None:
            self.id = action.name + "_" + "".join(random.choice("0123456789") for _ in range(8))

        self._create_options = create_options
        self._get_settings = get_settings
        self._get_src = get_src
        self._get_dst = get_dst
        self._data_changed_cb = data_changed_cb
        self._need_preview = need_preview
        self._get_data = get_data

        self._src = []
        self._settings = {}
        self._dst = []

        self.output_meta = None
        self.postprocess_cb = postprocess_cb
        self.update_sources_cb = update_sources_cb

        md_description = self.action.md_description.replace(
            r"../../assets", r"https://raw.githubusercontent.com/supervisely/docs/master/assets"
        )

        # info option
        self._info_option = NodesFlow.Node.Option(
            name="sidebarNodeInfo",
            option_component=NodesFlow.SidebarNodeInfoOptionComponent(
                sidebar_template=Markdown(md_description, show_border=False).to_html(),
                sidebar_width=600,
            ),
        )
        # preview option
        self._preview_img_path = f"{g.STATIC_DIR}/{self.id}.jpg"
        self._preview_img_url = f"static/{self.id}.jpg"
        self._ann = None
        self._res_ann = None
        self._img_desc = None
        self._res_img_desc = None
        # self._preview_widget = LabeledImage(
        #     enable_zoom=True, empty_message="Click update to show preview image with labels"
        # )
        self._preview_widget = ImageAnnotationPreview(enable_zoom=True, line_width=1)
        self._preview_widget.hide()
        self._empty_preview_text = Text(
            "Click update to show preview image with labels", font_size=get_text_font_size()
        )
        _preview_container = Container(
            widgets=[self._empty_preview_text, self._preview_widget],
            gap=0,
            style="background: #f1f4f7; margin: 9px -5px -5px; padding: 15px 12px; border-radius: 8px;",
        )

        if self._need_preview:
            if custom_update_btn is not None:
                self._update_preview_button = custom_update_btn
            else:
                self._update_preview_button = Button(
                    text="Update",
                    icon="zmdi zmdi-refresh",
                    button_type="text",
                    button_size="small",
                    style=get_set_settings_button_style(),
                )

            if self.action.name == "images_project":
                if not isinstance(self.output_meta, ProjectMeta):
                    self._update_preview_button.disable()

            @self._update_preview_button.click
            def _update_preview_btn_click_cb():
                g.updater(("nodes", self.id))

        self._preview_options = []
        if self._need_preview:
            if self.action.name == "images_project":
                preview_text = NodesFlow.Node.Option(
                    name="update_preview_btn",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=get_set_settings_container(
                            Text("Preview Random Image", font_size=13), self._update_preview_button
                        )
                    ),
                )
            else:
                preview_text = NodesFlow.Node.Option(
                    name="update_preview_btn",
                    option_component=NodesFlow.WidgetOptionComponent(
                        widget=get_set_settings_container(
                            Text("Preview", font_size=get_text_font_size()),
                            self._update_preview_button,
                        )
                    ),
                )

            self._preview_options = [
                preview_text,
                # NodesFlow.Node.Option(
                #     name="preview",
                #     option_component=NodesFlow.WidgetOptionComponent(widget=_preview_container),
                # ),
                NodesFlow.Node.Option(
                    name="preview",
                    option_component=NodesFlow.WidgetOptionComponent(widget=_preview_container),
                ),
            ]

    def get_src(self) -> list:
        return self._src

    def get_dst(self) -> list:
        return self._dst

    def get_settings(self) -> dict:
        return self._settings

    # JSON
    def to_json(self) -> dict:
        return {
            "action": self.action.name,
            "src": self._src,  # always list
            "dst": self._dst[0] if len(self._dst) == 1 else self._dst,  # can be str if only one dst
            "settings": copy.deepcopy(self._settings),
        }

    def from_json(self, json_data: dict = {}) -> None:
        """Init src, dst and settings from json data"""
        src = json_data.get("src", [])
        if isinstance(src, str):
            src = [src]
        self._src = src
        dst = json_data.get("dst", [])
        if isinstance(dst, str):
            dst = [dst]
        self._dst = dst
        self._settings = json_data.get("settings", {})

    # NodesFlow.Node
    def create_node(self) -> NodesFlow.Node:
        """creates node from src, dst and settings"""
        self._inputs = self.action.create_inputs()
        self._outputs = self.action.create_outputs()
        options = self._create_options(src=self._src, dst=self._dst, settings=self._settings)

        def combine_options(options: list):
            result_options = [
                self._info_option,
            ]

            if not all([len(options[key]) == 0 for key in ["src", "dst", "settings"]]):
                result_options.append(get_separator(0))

            if len(options["src"]) > 0:
                result_options.extend(options["src"])
                result_options.append(get_separator(1))

            if len(options["dst"]) > 0:
                result_options.extend(options["dst"])
                result_options.append(get_separator(2))

            if len(options["settings"]) > 0:
                result_options.extend(options["settings"])

            if self._preview_options:
                result_options.append(get_separator(3))

            return [
                *result_options,
                *self._preview_options,
            ]

        return NodesFlow.Node(
            id=self.id,
            name=self.action.title,
            width=self.action.width,
            options=combine_options(options),
            inputs=self._inputs,
            outputs=self._outputs,
            inputs_up=True,
            header_color=None,
            header_text_color=None,
            icon=self.action.icon,
            icon_background_color=self.action.node_color,
        )

    def parse_options(self, node_options: dict):
        """Read node options and init src, dst and settings"""
        self._update_src(node_options)
        self._update_dst(node_options)
        self._update_settings(node_options)

    def update_sources(self, connections: List[tuple]):
        new_sources = []
        src_names = []
        for from_node_id, from_node_interface, to_node_interface in connections:
            src_name = self._connection_name(from_node_id, from_node_interface)
            src_names.append((src_name, to_node_interface))

        need_append = [True] * len(src_names)
        if self.update_sources_cb is not None:
            need_append = self.update_sources_cb(src_names)

        # fix var naming
        for (src_name, _), to_append in zip(src_names, need_append):
            if to_append:
                new_sources.append(src_name)

        if len(new_sources) > 0:
            self._src = new_sources

    def clear_preview(self):
        self._img_desc = None
        self._ann = None
        self._res_img_desc = None
        self._res_ann = None
        if self._need_preview:
            self._preview_widget.clean_up()
            self._preview_widget.hide()
            self._empty_preview_text.show()

    def set_src_img_desc(self, img_desc):
        self._img_desc = img_desc

    def set_src_ann(self, ann):
        self._ann = ann

    def get_src_img_desc(self):
        return self._img_desc

    def get_src_ann(self):
        return self._ann

    def get_preview_img_desc(self):
        if self._need_preview:
            return self._res_img_desc

    def update_preview(
        self, img_desc: ImageDescriptor, ann: Annotation, project_meta: ProjectMeta = None
    ):
        if project_meta is None:
            project_meta = self.output_meta
        if not self._need_preview:
            return
        self._res_img_desc = img_desc
        write_image(self._preview_img_path, self._res_img_desc.read_image())
        self._res_ann = ann
        # self._preview_widget.set(
        #     title=None, image_url=f"{self._preview_img_url}?{time.time()}", ann=self._res_ann
        # )
        self._preview_widget.set(
            image_url=f"{self._preview_img_url}?q={time.time()}",
            ann=self._res_ann,
            project_meta=project_meta,
        )

        # print(self._preview_widget.widget_id)

        if self._preview_widget.is_empty():
            self._preview_widget.hide()
            self._empty_preview_text.show()
        else:
            self._preview_widget.show()
            self._empty_preview_text.hide()
        os.environ["_SUPERVISELY_OFFLINE_FILES_UPLOADED"] = "False"

    def set_preview_loading(self, val: bool):
        if not self._need_preview:
            return
        self._preview_widget.loading = val
        self._update_preview_button.loading = val

    def get_ann(self):
        return self._res_ann

    def get_data(self):
        if self._get_data is None:
            return {}
        return self._get_data()

    def update_data(self, data: dict):
        if self._data_changed_cb is not None:
            self._data_changed_cb(**data)

    def update_project_meta(self, project_meta: ProjectMeta):
        if self._data_changed_cb is not None:
            self._data_changed_cb(**{"project_meta": project_meta})

    def modifies_data(self, modifies_data: bool):
        if self._data_changed_cb is not None:
            self._data_changed_cb(**{"modifies_data": modifies_data})

    # Utils
    def get_destination_name(self, dst_index: int):
        outputs = self.action.create_outputs()
        return outputs[dst_index].name

    def _connection_name(self, name: str, interface: str):
        interface_str = "_".join(
            [
                *[
                    part
                    for part in interface.split("_")
                    if part not in ["", "source", "destination", "input", "output"]
                ],
            ]
        )
        return "$" + name + (f"__{interface_str}" if interface_str else "")

    def _create_destinations(self):
        return [self._connection_name(self.id, output.name) for output in self._outputs]

    def _update_src(self, node_options: dict):
        if self._get_src is not None:
            self._src = self._get_src(options_json=node_options)
        else:
            self._src = []

    def _update_dst(self, node_options: dict):
        """Read node options and init dst"""
        if self._get_dst is not None:
            self._dst = self._get_dst(options_json=node_options)
        else:
            self._dst = self._create_destinations()

    def _update_settings(self, node_options: dict):
        """Read node options and init settings"""
        if self._get_settings is not None:
            self._settings = self._get_settings(options_json=node_options)
        else:
            self._settings = {}
