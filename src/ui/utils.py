import json

from supervisely.app.widgets import Container, Flexbox, FileThumbnail, ProjectThumbnail, Text
from supervisely import ProjectMeta
from supervisely.app.content import StateJson, DataJson
from supervisely.api.labeling_job_api import LabelingJobInfo

import supervisely as sly

from src.utils import (
    LegacyProjectItem,
    get_project_by_name,
    get_project_meta,
    download_preview,
    update_project_info,
)
from src.compute.Net import Net
from src.compute.Layer import Layer as NetLayer
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from src.ui.dtl import actions_dict, actions_list
from src.ui.dtl.Action import Action, SourceAction
from src.ui.dtl.Layer import Layer
from src.ui.dtl import (
    SAVE_ACTIONS,
    PIXEL_LEVEL_TRANSFORMS,
    SPATIAL_LEVEL_TRANSFORMS,
    ANNOTATION_TRANSFORMS,
    OTHER,
)
from src.exceptions import (
    BadSettingsError,
    CustomException,
    ActionNotFoundError,
    LayerNotFoundError,
)
import src.globals as g
import src.utils as utils


def find_layer_id_by_dst(dst: str):
    for layer_id, layer in g.layers.items():
        if dst in layer.get_dst():
            return layer_id
    return None


def find_children(parent: Layer, all_layers_ids: list):
    children = []
    parent_dst = parent.get_dst()
    for layer_id in all_layers_ids:
        layer = g.layers.get(layer_id)
        for l_src in layer.get_src():
            if l_src in parent_dst:
                children.append(layer_id)
    return children


def init_layers(nodes_state: dict):
    data_layers_ids = []
    save_layers_ids = []
    transform_layers_ids = []
    all_layers_ids = []
    for node_id, node_options in nodes_state.items():
        try:
            layer = g.layers[node_id]
            layer: Layer
        except KeyError:
            raise LayerNotFoundError(node_id)

        try:
            layer.parse_options(node_options)
        except CustomException as e:
            e.message = f"Error parsing options: {e.message}"
            e.extra["action_name"] = layer.action.name
            raise e
        except Exception as e:
            raise CustomException(
                f"Error parsing options",
                error=e,
                extra={"action_name": layer.action.name},
            )

        if issubclass(layer.action, SourceAction):
            data_layers_ids.append(node_id)
        if layer.action.name in actions_list[SAVE_ACTIONS]:
            save_layers_ids.append(node_id)
        if layer.action.name in [
            action
            for group in (
                PIXEL_LEVEL_TRANSFORMS,
                SPATIAL_LEVEL_TRANSFORMS,
                ANNOTATION_TRANSFORMS,
                OTHER,
            )
            for action in actions_list.get(group, [])
        ]:
            transform_layers_ids.append(node_id)
        all_layers_ids.append(node_id)

    return {
        "data_layers_ids": data_layers_ids,
        "save_layers_ids": save_layers_ids,
        "transformation_layers_ids": transform_layers_ids,
        "all_layers_ids": all_layers_ids,
    }


def init_src(edges: list):
    for edge in edges:
        from_node_id = edge["output"]["node"]
        from_node_interface = edge["output"]["interface"]
        to_node_id = edge["input"]["node"]
        try:
            layer = g.layers[to_node_id]
        except KeyError:
            raise LayerNotFoundError(to_node_id)
        layer: Layer
        # if source already in layer -> pass
        layer.add_source(from_node_id, from_node_interface)


def init_nodes_state(
    net: Net, data_layers_ids: list, all_layers_ids: list, nodes_state: dict, edges: list
):
    """Update nodes project meta and data"""

    def calc_metas(net):
        # Call meta changed callbacks for Data layers
        for layer_id in data_layers_ids:
            layer = g.layers[layer_id]
            layer: Layer
            src = layer.get_src()
            layer_input_meta = ProjectMeta()
            if src:
                project_name, _ = src[0].split("/")
                layer_input_meta = utils.get_project_meta(
                    utils.get_project_by_name(project_name).id
                )
            layer.update_project_meta(layer_input_meta)

        cur_level_layers_idxs = {
            idx for idx, layer in enumerate(net.layers) if layer.type == "data" or not layer.srcs
        }
        metas_dict = {}
        for data_layer_idx in cur_level_layers_idxs:
            data_layer = net.layers[data_layer_idx]
            try:
                input_meta = data_layer.in_project_meta
            except AttributeError:
                input_meta = ProjectMeta()
            except KeyError:
                input_meta = ProjectMeta()
            for src in data_layer.srcs:
                metas_dict[src] = input_meta

        def get_dest_layers_idxs(the_layer_idx):
            the_layer = net.layers[the_layer_idx]
            return [
                idx
                for idx, dest_layer in enumerate(net.layers)
                if len(set(the_layer.dsts) & set(dest_layer.srcs)) > 0
            ]

        def layer_input_metas_are_calculated(the_layer_idx):
            the_layer = net.layers[the_layer_idx]
            return all((x in metas_dict for x in the_layer.srcs))

        datas_dict = {}
        processed_layers = set()
        while len(cur_level_layers_idxs) != 0:
            next_level_layers_idxs = set()

            for cur_layer_idx in cur_level_layers_idxs:
                cur_layer = net.layers[cur_layer_idx]
                processed_layers.add(cur_layer_idx)
                # TODO no need for dict here?
                cur_layer_input_metas = {src: metas_dict[src] for src in cur_layer.srcs}

                # update ui layer meta and data
                merged_meta = utils.merge_input_metas(cur_layer_input_metas.values())
                ui_layer_id = all_layers_ids[cur_layer_idx]
                ui_layer = g.layers[ui_layer_id]
                ui_layer: Layer
                merged_data = {}
                # gather data from all sources
                for src in ui_layer.get_src():
                    merged_data.update(datas_dict.get(find_layer_id_by_dst(src), {}))
                # update data in node
                ui_layer.update_data({**merged_data, "project_meta": merged_meta})
                # get update data to use in next nodes
                merged_data.update(ui_layer.get_data())
                datas_dict[ui_layer_id] = merged_data

                # update settings according to new meta
                node_options = nodes_state.get(ui_layer_id, {})
                ui_layer.parse_options(node_options)
                init_src(edges)
                ui_layer = g.layers[ui_layer_id]

                # update net layer with new settings
                layer_config = ui_layer.to_json()
                action = layer_config["action"]
                if action not in NetLayer.actions_mapping:
                    raise ActionNotFoundError(action)
                layer_cls = NetLayer.actions_mapping[action]
                if layer_cls.type == "data":
                    layer = layer_cls(layer_config, net=net)
                elif layer_cls.type == "processing":
                    layer = layer_cls(layer_config, net=net)
                elif layer_cls.type == "save":
                    layer = layer_cls(layer_config, g.RESULTS_DIR, net=net)
                    net.save_layer = layer
                net.layers[cur_layer_idx] = layer

                # calculate output meta of current net layer
                cur_layer = net.layers[cur_layer_idx]
                cur_layer_res_meta = cur_layer.make_output_meta(cur_layer_input_metas)

                # update output meta of current ui layer
                ui_layer.output_meta = cur_layer_res_meta

                for dst in cur_layer.dsts:
                    metas_dict[dst] = cur_layer_res_meta

                # yield cur_layer_res_meta, cur_layer_idx

                dest_layers_idxs = get_dest_layers_idxs(cur_layer_idx)
                for next_candidate_idx in dest_layers_idxs:
                    if layer_input_metas_are_calculated(next_candidate_idx):
                        next_level_layers_idxs.update([next_candidate_idx])

            cur_level_layers_idxs = next_level_layers_idxs

        return processed_layers

    processed_layers = calc_metas(net)
    for layer_idx in range(len(net.layers)):
        if layer_idx not in processed_layers:
            ui_layer_id = all_layers_ids[layer_idx]
            ui_layer = g.layers[ui_layer_id]
            ui_layer.update_data({"project_meta": ProjectMeta()})
    return net


def get_layer_parents_chain(layer_id: str, chain: list = None):
    if chain is None:
        chain = []
    layer: Layer = g.layers[layer_id]
    chain.append(layer_id)
    if layer.get_preview_img_desc() is not None:
        return chain
    if issubclass(layer.action, SourceAction):
        return chain
    src_layers = [find_layer_id_by_dst(src) for src in layer.get_src()]
    for src_layer in src_layers:
        if src_layer is None:
            continue
        if src_layer in chain:
            continue
        return get_layer_parents_chain(src_layer, chain)
    return chain


def get_layer_children_list(
    layer_id: str,
    all_layers_ids: list,
    layers: list = None,
):
    if layers is None:
        layers = []
    if layer_id in layers:
        return layers
    layers.append(layer_id)
    layer: Layer = g.layers[layer_id]
    for child in find_children(layer, all_layers_ids):
        get_layer_children_list(child, all_layers_ids, layers)
    return layers


def load_preview_for_data_layer(layer: Layer):
    src = layer.get_src()
    if src is None or len(src) == 0:
        return None, None

    project_name, dataset_name = src[0].split("/")
    try:
        project_info = get_project_by_name(project_name)
        project_meta = get_project_meta(project_info.id)
    except Exception as e:
        raise CustomException(
            f"Error getting project meta", error=e, extra={"project_name": project_name}
        )

    if layer.action.name == "input_labeling_job":
        layer_settings = layer.get_settings()
        items_ids = layer_settings.get("entities_ids", None)
    else:
        items_ids = None

    try:
        item_info, preview_img_path, preview_ann_path = download_preview(
            project_name, dataset_name, project_meta, g.MODALITY_TYPE, items_ids
        )
    except Exception as e:
        raise CustomException(
            f"Error downloading image and annotation for preview",
            error=e,
            extra={"project_name": project_name, "dataset_name": dataset_name},
        )
    preview_img = sly.image.read(preview_img_path)
    with open(preview_ann_path, "r") as f:
        preview_ann = sly.Annotation.from_json(json.load(f), project_meta)
    preview_path = f"{g.PREVIEW_DIR}/{layer.id}"
    img_desc = ImageDescriptor(
        LegacyProjectItem(
            project_name=project_name,
            ds_name=dataset_name,
            item_name="preview_image",
            item_info=item_info,
            ia_data={"item_ext": ".jpg"},
            item_path=f"{preview_path}/preview_image.jpg",
            ann_path=f"{preview_path}/preview_ann.json",
        ),
        False,
    )
    img_desc = img_desc.clone_with_item(preview_img)
    img_desc.write_image_local(f"{preview_path}/preview_image.jpg")
    layer.set_src_img_desc(img_desc)
    layer.set_src_ann(preview_ann)
    return img_desc, preview_ann


def update_preview(net: Net, data_layers_ids: list, all_layers_ids: list, layer_id: str):
    # disable preview if "videos"
    if net.modality == "videos":
        return

    layer = g.layers[layer_id]
    layer.clear_preview()

    try:
        layer_idx = all_layers_ids.index(layer_id)
    except:
        # hack, fix later
        g.layers.pop(layer_id)
        return

    net.preview_mode = True
    net.calc_metas()
    net.preprocess()

    layer = g.layers[layer_id]

    layer.clear_preview()
    children = get_layer_children_list(layer_id, all_layers_ids)
    if children:
        for l_id in children:
            g.layers[l_id].clear_preview()

    layers_id_chain = None  # parents chain
    if issubclass(layer.action, SourceAction):
        img_desc, preview_ann = load_preview_for_data_layer(layer)
    # if layer has no sources, clean preview
    elif not layer.get_src():
        return
    else:
        img_desc = layer.get_src_img_desc()
        preview_ann = layer.get_src_ann()
        if img_desc is None:
            # try previous layer
            layers_id_chain = get_layer_parents_chain(layer.id)
            if len(layers_id_chain) == 0:
                return
            if len(layers_id_chain) == 1:
                start_layer_id = layers_id_chain[0]
            else:
                start_layer_id = layers_id_chain[-2]
            layer_idx = all_layers_ids.index(start_layer_id)
            source_layer_id = layers_id_chain[-1]
            source_layer = g.layers[source_layer_id]
            if (
                issubclass(source_layer.action, SourceAction)
                and source_layer.get_preview_img_desc() is None
            ):
                img_desc, preview_ann = load_preview_for_data_layer(source_layer)
            else:
                img_desc = source_layer.get_preview_img_desc()
                preview_ann = source_layer.get_ann()
    if img_desc is None:
        raise BadSettingsError(
            "Cannot load preview image for input layer. Check that you selected input project and nodes are connected"
        )

    data_el = (img_desc, preview_ann)
    if layers_id_chain is None:
        layers_idx_whitelist = None
    else:
        children = get_layer_children_list(layer_id, all_layers_ids)
        layers_idx_whitelist = [all_layers_ids.index(id) for id in layers_id_chain]
        layers_idx_whitelist.extend([all_layers_ids.index(id) for id in children])
    processing_generator = net.start_iterate(
        data_el, layer_idx=layer_idx, layers_idx_whitelist=layers_idx_whitelist
    )
    updated = set()
    is_starting_layer = True
    prev_img_desc = None
    prev_ann = None
    try:
        for data_el, layer_indx in processing_generator:
            if layer_indx in updated:
                continue
            layer = g.layers[all_layers_ids[layer_indx]]
            layer: Layer
            if len(data_el) == 1:
                img_desc, ann = data_el[0]
            elif len(data_el) == 3:
                img_desc, ann, _ = data_el
            else:
                img_desc, ann = data_el
            if not is_starting_layer:
                layer.set_src_img_desc(prev_img_desc)
                layer.set_src_ann(prev_ann)
            prev_img_desc = img_desc
            prev_ann = ann
            layer.update_preview(img_desc, ann)
            layer.set_preview_loading(False)
            is_starting_layer = False
            updated.add(layer_indx)
    except Exception as e:
        sly.logger.error(f"Error updating preview", exc_info=str(e))
    net.preview_mode = False
    # ^?remove?^


def update_all_previews(net: Net, data_layers_ids: list, all_layers_ids: list):
    # disable preview if "videos"
    if net.modality == "videos":
        return

    for layer in g.layers.values():
        layer.clear_preview()
    updated = set()

    net.preview_mode = True
    net.calc_metas()
    net.preprocess()

    for data_layer_id in data_layers_ids:
        data_layer = g.layers[data_layer_id]
        src = data_layer.get_src()
        if src is None or len(src) == 0:
            # Skip if no sources specified for data layer
            continue

        project_name, dataset_name = src[0].split("/")
        try:
            project_info = get_project_by_name(project_name)
            project_meta = get_project_meta(project_info.id)
        except Exception as e:
            raise CustomException(
                f"Error getting project meta", error=e, extra={"project_name": project_name}
            )

        try:
            if net.modality == "images":
                item_info, preview_img_path, preview_ann_path = download_preview(
                    project_name, dataset_name, project_meta
                )
            elif net.modality == "videos":
                item_info, preview_img_path, preview_ann_path = download_preview(
                    project_name, dataset_name, project_meta, "videos"
                )
            else:
                raise NotImplementedError(f"Modality {net.modality} is not supported yet")
        except Exception as e:
            raise CustomException(
                f"Error downloading image and annotation for preview",
                error=e,
                extra={"project_name": project_name, "dataset_name": dataset_name},
            )
        preview_img = sly.image.read(preview_img_path)
        with open(preview_ann_path, "r") as f:
            preview_ann = sly.Annotation.from_json(json.load(f), project_meta)
        preview_path = f"{g.PREVIEW_DIR}/{data_layer.id}"
        img_desc = ImageDescriptor(
            LegacyProjectItem(
                project_name=project_name,
                ds_name=dataset_name,
                item_name="preview_image",
                item_info=item_info,
                ia_data={"item_ext": ".jpg"},
                item_path=f"{preview_path}/preview_image.jpg",
                ann_path=f"{preview_path}/preview_ann.json",
            ),
            False,
        )
        img_desc = img_desc.clone_with_item(preview_img)
        img_desc.write_image_local(f"{preview_path}/preview_image.jpg")

        data_el = (img_desc, preview_ann)

        processing_generator = net.start_iterate(data_el)
        for data_el, layer_indx in processing_generator:
            if layer_indx in updated:
                continue
            layer = g.layers[all_layers_ids[layer_indx]]
            layer: Layer
            if len(data_el) == 1:
                img_desc, ann = data_el[0]
            elif len(data_el) == 3:
                img_desc, ann, _ = data_el
            else:
                img_desc, ann = data_el
            layer.update_preview(img_desc, ann)
            layer.set_preview_loading(False)
            updated.add(layer_indx)
    net.preview_mode = False
    # ^?remove?^


def create_results_widget(file_infos, supervisely_layers, labeling_job_layers):
    widgets = []
    if len(file_infos) > 0:
        widgets.append(
            Flexbox(
                widgets=[
                    Text("Archives: "),
                    *[FileThumbnail(file_info) for file_info in file_infos],
                ]
            )
        )
    if len(supervisely_layers) > 0:
        widgets.append(
            Flexbox(
                widgets=[
                    Text("Projects: "),
                    *[
                        ProjectThumbnail(update_project_info(l.sly_project_info))
                        for l in supervisely_layers
                    ],
                ]
            )
        )
    if len(labeling_job_layers) > 0:
        labeling_job_text_widgets = []
        for l in labeling_job_layers:
            for lj_info in l.created_labeling_jobs:
                lj_info: LabelingJobInfo
                w = Text(
                    f'<a href="{g.api.server_address}/labeling/jobs/{lj_info.id}/stats" target="_blank">{lj_info.name}</a>'
                )
                labeling_job_text_widgets.append(w)

        if len(labeling_job_text_widgets) == 0:
            labeling_job_text_widgets.append(Text("No labeling jobs created. Check settings."))

        widgets.append(
            Container(
                widgets=[
                    Text("Labeling jobs: "),
                    *labeling_job_text_widgets,
                ]
            )
        )
    return Container(widgets=widgets)


def get_layer_id(action_name: str):
    g.layers_count += 1
    id = action_name + "_" + str(g.layers_count)
    return id


def register_layer(layer: Layer):
    g.layers[layer.id] = layer


def create_new_layer(
    action_name: str,
) -> Layer:
    try:
        action = actions_dict[action_name]
    except KeyError:
        raise ActionNotFoundError(action_name)
    id = get_layer_id(action_name)
    action: Action
    try:
        layer = action.create_new_layer(id)
    except CustomException as e:
        e.extra["action_name"] = action_name
    except Exception as e:
        raise e
    register_layer(layer)
    StateJson().send_changes()
    DataJson().send_changes()
    return layer


def create_node(layer: Layer, position=None):
    try:
        node = layer.create_node()
    except CustomException as e:
        e.extra["layer_config"] = layer.to_json()
        raise e
    except Exception as e:
        raise e
    node.set_position(position)
    return node


def show_error(message: str, error: CustomException):
    description = str(error)
    if error.extra:
        g.error_extra_literal.show()
        extra_text = json.dumps(error.extra, indent=4)
    else:
        g.error_extra_literal.hide()
        extra_text = ""
    g.error_dialog.title = message
    g.error_description.text = description
    g.error_extra.set_text(extra_text)
    g.error_dialog.show()
