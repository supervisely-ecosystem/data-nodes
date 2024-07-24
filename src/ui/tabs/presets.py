import random
import json
from time import sleep

from supervisely.app.widgets import (
    Button,
    Container,
    CheckboxField,
    Input,
    Field,
    Select,
    OneOf,
    Empty,
    FileThumbnail,
    Dialog,
    Text,
)
from supervisely.app import show_dialog
from supervisely import logger
from src.compute.Net import Net
from src.ui.dtl.Layer import Layer
from src.ui.dtl.Action import SourceAction
from src.ui.dtl import actions_list, actions_dict_legacy
from src.ui.dtl import SOURCE_ACTIONS
from src.ui.tabs.configure import nodes_flow
import src.ui.utils as ui_utils
import src.utils as utils
import src.globals as g
from src.exceptions import handle_exception
from src.exceptions import CustomException, BadSettingsError

preset_name_input = Input(value="preset", placeholder="Enter preset name")
save_as_template_checkbox = CheckboxField(
    title="Save as template",
    description=f"Presets saved as templates will use the current '{g.MODALITY_TYPE.capitalize()} Project' layers with the selected project and dataset(s)",
    checked=False,
)
save_preset_btn = Button("Save", icon="zmdi zmdi-floppy")
save_preset_file_thumbnail = FileThumbnail()
save_preset_file_thumbnail.hide()
save_notification_saved = Text("Preset has been successfully saved", status="success")
save_notification_empty_name = Text("Preset name is empty", status="error")
save_notification_select = Select(
    items=[
        Select.Item("empty", content=Empty()),
        Select.Item("saved", content=save_notification_saved),
        Select.Item("empty_name", content=save_notification_empty_name),
    ]
)
save_notification_oneof = OneOf(save_notification_select)
save_container = Container(
    widgets=[
        Field(
            title="Preset name",
            description=f'Preset will be saved to folder "{g.PRESETS_PATH}" in your Team files with .json extension',
            content=preset_name_input,
        ),
        save_as_template_checkbox,
        save_preset_btn,
        save_notification_oneof,
        save_preset_file_thumbnail,
    ]
)


load_file_selector = Select(items=[], filterable=True)
load_preset_btn = Button("Load")
load_notification_loaded = Text("Preset loaded", status="success")
load_notification_file_not_selected = Text("File not selected", status="error")
load_notification_file_multiple = Text("Select maximum one preset", status="error")
load_notification_error = Text("Error loading preset", status="error")
load_notification_no_presets = Text("No presets found", status="info")
load_notification_no_presets.hide()
load_notification_select = Select(
    items=[
        Select.Item("empty", content=Empty()),
        Select.Item("loaded", content=load_notification_loaded),
        Select.Item("not selected", content=load_notification_file_not_selected),
        Select.Item("multiple", content=load_notification_file_multiple),
        Select.Item("error", content=load_notification_error),
    ]
)
load_notification_oneof = OneOf(load_notification_select)
load_container = Container(
    widgets=[
        Field(
            title="Select preset",
            description=f'Presets are stored in folder "{g.PRESETS_PATH}" in your Team files',
            content=load_file_selector,
        ),
        load_notification_no_presets,
        load_preset_btn,
        load_notification_oneof,
    ]
)

save_layout = Container(widgets=[save_container], gap=0)
load_layout = Container(widgets=[load_container], gap=0)
save_dialog = Dialog(title="Save Preset", content=save_layout)
load_dialog = Dialog(title="Load Preset", content=load_layout)


@save_preset_btn.click
def save_json_button_cb():
    is_save_as_template = save_as_template_checkbox.is_checked()

    edges = nodes_flow.get_edges_json()
    nodes_state = nodes_flow.get_nodes_state_json()

    nodes_json = nodes_flow.get_nodes_json()

    # save node order position
    scene_location = []
    for idx, node_json in enumerate(nodes_json):
        scene_location.append({"order_idx": idx, "position": node_json["position"]})

    # Init layers data
    layers_ids = ui_utils.init_layers(nodes_state)
    all_layers_ids = layers_ids["all_layers_ids"]

    ui_utils.init_src(edges)

    dtl_json = [g.layers[layer_id].to_json() for layer_id in all_layers_ids]
    if is_save_as_template:
        for idx, layer_json in enumerate(dtl_json):
            if layer_json["action"] == f"{g.MODALITY_TYPE}_project":
                dtl_json[idx]["is_template"] = True

    # @TODO: make more safe position save by checking id and names
    for idx, layer_json in enumerate(dtl_json):
        layer_json["scene_location"] = scene_location[idx]

    preset_name = preset_name_input.get_value()
    if preset_name == "":
        save_notification_select.set_value("empty_name")
        return

    # dst_path = f"/{g.TEAM_FILES_PATH}/presets/{preset_name}.json"
    if is_save_as_template:
        dst_path = f"{g.PRESETS_PATH}/{preset_name} (template).json"
    else:
        dst_path = f"{g.PRESETS_PATH}/{preset_name}.json"
    if g.api.file.exists(g.TEAM_ID, dst_path):
        dst_path = g.api.file.get_free_name(g.TEAM_ID, dst_path)
    src_path = g.DATA_DIR + "/preset.json"
    utils.create_data_dir()
    with open(src_path, "w") as f:
        json.dump(dtl_json, f, indent=4)
    file_info = g.api.file.upload(g.TEAM_ID, src_path, dst_path)
    save_preset_file_thumbnail.set(file_info)
    save_preset_file_thumbnail.show()
    save_notification_select.set_value("saved")
    # clean input name after saving
    preset_name_input.set_value("")


@preset_name_input.value_changed
def preset_name_input_cb(value):
    if value == "":
        save_notification_select.set_value("empty_name")
        save_preset_btn.disable()
    else:
        save_notification_select.set_value("empty")
        save_preset_btn.enable()


def load_json():
    load_preset_btn.loading = True
    load_file_selector.disable()
    load_notification_select.set_value("empty")
    preset_loaded = True

    filename = load_file_selector.get_value()
    logger.info(f"Loading preset: {filename}")
    if filename is None:
        load_notification_select.set_value("not selected")
        load_preset_btn.loading = False
        load_file_selector.enable()
        return
    # path =f"/{g.TEAM_FILES_PATH}/presets/{filename}.json"
    path = f"{g.PRESETS_PATH}/{filename}.json"
    nodes_flow.clear()
    g.layers.clear()
    try:
        utils.create_data_dir()
        g.api.file.download(g.TEAM_ID, path, g.DATA_DIR + "/preset.json")
        with open(g.DATA_DIR + "/preset.json", "r") as f:
            dtl_json = json.load(f)
        apply_json(dtl_json)
    except Exception as e:
        load_notification_error.description = f'Error loading preset from "{path}". {str(e)}'
        load_notification_select.set_value("error")
        preset_loaded = False
    finally:
        load_preset_btn.loading = False
        load_file_selector.enable()
    if preset_loaded:
        load_notification_select.set_value("loaded")
        load_dialog.hide()


def apply_json(dtl_json):
    g.stop_updates = True
    try:
        # create layer objects
        ids = []
        data_layers_ids = []
        template_id = 0
        for idx, layer_json in enumerate(dtl_json):
            is_template = False
            original_action_name = layer_json.get("action", None)
            action_name = layer_json.get("action", None)
            if original_action_name is None:
                raise BadSettingsError(
                    'Missing "action" field in layer config', extra={"layer_config": layer_json}
                )

            legacy_action_name = actions_dict_legacy.get(original_action_name, None)
            if legacy_action_name is not None:
                action_name = legacy_action_name
            else:
                action_name = original_action_name

            if action_name == f"{g.MODALITY_TYPE}_project":
                is_template = layer_json.get("is_template", False)

            dtl_json[idx]["action"] = dtl_json[idx]["action"].replace(
                original_action_name, action_name
            )
            for i, src in enumerate(dtl_json[idx]["src"]):
                if src.startswith("$"):
                    src_action_name = src[1:].rsplit("_", 1)[0]
                else:
                    if is_template:
                        if len(g.current_srcs) > 0:
                            for idx, k in enumerate(g.current_srcs):
                                if idx == template_id:
                                    dtl_json[idx]["src"] = g.current_srcs[k][0]
                                    src_action_name = g.current_srcs[k][0]
                                    template_id += 1
                                    break
                        else:
                            logger.warn("Couldn't find current project source")
                            src_action_name = src
                    else:
                        src_action_name = src  # use if SourceAction
                if src_action_name in actions_dict_legacy:
                    dtl_json[idx]["src"][i] = dtl_json[idx]["src"][i].replace(
                        src_action_name, actions_dict_legacy[src_action_name]
                    )
            if isinstance(dtl_json[idx]["dst"], list):
                for i, dst in enumerate(dtl_json[idx]["dst"]):
                    if dst in actions_dict_legacy:
                        dtl_json[idx]["dst"][i] = dtl_json[idx]["dst"][i].replace(
                            dst, actions_dict_legacy[dst]
                        )
            else:
                dtl_json[idx]["dst"] = dtl_json[idx]["dst"].replace(
                    original_action_name, action_name
                )

            settings = layer_json.get("settings", None)
            if settings is None:
                raise BadSettingsError(
                    'Missing "settings" field in layer config', extra={"layer_config": layer_json}
                )

            layer = ui_utils.create_new_layer(action_name)
            layer.init_widgets()
            ids.append(layer.id)
            if action_name in actions_list[SOURCE_ACTIONS] or action_name == "filtered_project":
                data_layers_ids.append(layer.id)

        # update src and dst
        for i, layer_id in enumerate(ids):
            layer_json = dtl_json[i]
            layer = g.layers[layer_id]
            layer: Layer

            src = layer_json.get("src", [])
            if type(src) is str:
                src = [src]
            if g.PROJECT_ID and issubclass(layer.action, SourceAction):
                ds = "*"
                if g.DATASET_ID:
                    ds = g.api.dataset.get_info_by_id(g.DATASET_ID).name
                pr = g.api.project.get_info_by_id(g.PROJECT_ID).name
                src = [f"{pr}/{ds}"]
                layer_json["src"] = src

            layer._src = src

            dst = layer_json.get("dst", [])
            if type(dst) is str:
                dst = [dst]
            layer._dst = dst

        # update settings
        for i, layer_id in enumerate(ids):
            layer_json = dtl_json[i]
            layer = g.layers[layer_id]
            layer.from_json(layer_json)

        # init metas for data layers
        for i, layer_id in enumerate(data_layers_ids):
            data_layer = g.layers[layer_id]
            src = data_layer.get_src()
            if len(src) == 0:
                # Skip if no sources specified for data layer
                show_dialog(
                    title="Empty source",
                    description=f"Project is not specified for {data_layer.action.title} layer. Please select the project manually in the layer card",
                    status="info",
                )
                continue

            # Add project meta
            try:
                project_name, dataset_name = src[0].split("/")
            except:
                show_dialog(
                    title="Bad source",
                    description=f'Wrong source path for {data_layer.action.title} layer. Should be "project_name/dataset_name" or "project_name/*". Please select the project manually in the layer card',
                    status="error",
                )
                continue
            try:
                project_info = utils.get_project_by_name(project_name)
                project_meta = utils.get_project_meta(project_info.id)
            except Exception as e:
                show_dialog(
                    "Source not found",
                    description=f'Cannot find project "{project_name}". Please select the project manually in the layer card',
                    status="error",
                )
                continue
            data_layer.update_project_meta(project_meta)

        # init metas for all layers
        net = Net(dtl_json, g.RESULTS_DIR, g.MODALITY_TYPE)
        net.calc_metas()
        for layer_id, net_layer in zip(ids, net.layers):
            layer = g.layers[layer_id]
            layer: Layer
            layer.output_meta = net_layer.output_meta

        for layer_id in ids:
            if layer_id in data_layers_ids:
                continue
            layer = g.layers[layer_id]

            output_metas_to_merge = []

            layer_sources = layer.get_src()
            if isinstance(layer_sources, dict):
                for k in layer_sources:
                    for src in layer_sources[k]:
                        src_layer = g.layers[ui_utils.find_layer_id_by_dst(src)]
                        output_metas_to_merge.append(src_layer.output_meta)
            else:
                for src in layer_sources:
                    src_layer = g.layers[ui_utils.find_layer_id_by_dst(src)]
                    output_metas_to_merge.append(src_layer.output_meta)

            layer_input_meta = utils.merge_input_metas(output_metas_to_merge)
            layer.update_project_meta(layer_input_meta)

        # create nodes
        for idx, layer_id in enumerate(ids):
            layer = g.layers[layer_id]
            layer_json = layer.to_json()
            node = layer.create_node()

            # set position
            position = None
            # @TODO: make more safe position retrieve by checking id and names
            scene_location = dtl_json[idx].get("scene_location", None)
            if scene_location is not None:
                position = scene_location.get("position", None)

            node.set_position(position)
            nodes_flow.add_node(node)

        # create node connections
        nodes_flow_edges = []
        for dst_layer_id in ids:
            dst_layer = g.layers[dst_layer_id]
            dst_layer: Layer
            dst_layer_sources = dst_layer.get_src()
            if isinstance(dst_layer_sources, dict):
                for k in dst_layer_sources:
                    for src in dst_layer_sources[k]:
                        for src_layer_id in ids:
                            src_layer = g.layers[src_layer_id]
                            for dst_idx, dst in enumerate(src_layer.get_dst()):
                                if dst == src:
                                    try:
                                        nodes_flow_edges.append(
                                            {
                                                "id": random.randint(
                                                    10000000000000, 99999999999999
                                                ),
                                                "output": {
                                                    "node": src_layer_id,
                                                    "interface": src_layer.get_destination_name(
                                                        dst_idx
                                                    ),
                                                },
                                                "input": {
                                                    "node": dst_layer_id,
                                                    "interface": k,
                                                },
                                            }
                                        )
                                    except:
                                        pass
            else:
                for src in dst_layer_sources:
                    for src_layer_id in ids:
                        src_layer = g.layers[src_layer_id]
                        for dst_idx, dst in enumerate(src_layer.get_dst()):
                            if dst == src:
                                try:
                                    nodes_flow_edges.append(
                                        {
                                            "id": random.randint(10000000000000, 99999999999999),
                                            "output": {
                                                "node": src_layer_id,
                                                "interface": src_layer.get_destination_name(
                                                    dst_idx
                                                ),
                                            },
                                            "input": {
                                                "node": dst_layer_id,
                                                "interface": "source",
                                            },
                                        }
                                    )
                                except:
                                    pass
        nodes_flow.set_edges(nodes_flow_edges)
        g.stop_updates = False
        g.updater(("nodes", None))
        sleep(1.5)  # delay for previews to load
    finally:
        g.stop_updates = False


@load_preset_btn.click
@handle_exception
def load_json_button_cb():
    g.updater("load_json")


def update_load_dialog():
    load_notification_select.set_value("empty")
    load_file_selector.loading = True
    presets_infos = g.api.file.list(g.TEAM_ID, g.PRESETS_PATH, return_type="fileinfo")
    load_file_selector.set(
        items=[Select.Item(".".join(info.name.split(".")[:-1])) for info in presets_infos]
    )
    if len(presets_infos) == 0:
        load_notification_no_presets.show()
        load_file_selector.hide()
    else:
        load_notification_no_presets.hide()
        load_file_selector.show()
    load_file_selector.loading = False


def update_save_dialog():
    save_preset_file_thumbnail.hide()
