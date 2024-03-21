# coding: utf-8

import os
import json

import numpy as np

from supervisely import Annotation, ProjectMeta, VideoAnnotation, KeyIdMap

from src.compute.Layer import Layer
from src.compute import layers  # to register layers
from src.compute.dtl_utils.item_descriptor import ImageDescriptor, VideoDescriptor
from src.utils import (
    get_project_by_name,
    get_dataset_by_name,
    get_all_datasets,
    get_project_meta,
    get_dataset_by_id,
    get_project_by_id,
)
from src.ui.widgets import CircleProgress
import src.globals as g
from src.utils import LegacyProjectItem
from src.exceptions import (
    ActionNotFoundError,
    BadSettingsError,
    CreateMetaError,
    GraphError,
    CustomException,
)

from supervisely.io.fs import get_file_ext


class Net:
    def __init__(self, graph_desc, output_folder, modality):
        self.layers = []
        self.preview_mode = False
        self.modality = modality

        if type(graph_desc) is str:
            graph_path = graph_desc

            if not os.path.exists(graph_path):
                raise RuntimeError('No such config file "%s"' % graph_path)
            else:
                self.graph = json.load(open(graph_path, "r"))
        else:
            self.graph = graph_desc

        for layer_config in self.graph:
            if "action" not in layer_config:
                raise BadSettingsError(
                    'Missing "action" field in layer config', extra={"layer_config": layer_config}
                )
            action = layer_config["action"]
            if action not in Layer.actions_mapping:
                raise ActionNotFoundError(action)
            layer_cls = Layer.actions_mapping[action]
            if layer_cls.type == "data":
                layer = layer_cls(layer_config, net=self)
            elif layer_cls.type == "processing":
                layer = layer_cls(layer_config, net=self)
            elif layer_cls.type == "save":
                layer = layer_cls(layer_config, output_folder, net=self)
                self.save_layer = layer
            else:
                raise NotImplementedError()
            self.layers.append(layer)

        self.flat_out_names = False  # @TODO: move out
        self.annot_archive = None
        self.reset_existing_names()

    def validate(self, circle_progress: CircleProgress):
        graph_has_datal = False
        graph_has_savel = False
        for layer in self.layers:
            layer: Layer
            try:
                layer.validate()
            except CustomException as e:
                e.extra["layer_config"] = layer.config
                raise e
            except:
                raise

            if type(layer).type == "data":
                graph_has_datal = True
            elif type(layer).type == "processing":
                pass
            elif type(layer).type == "save":
                graph_has_savel = True

        if graph_has_datal is False:
            raise GraphError(
                "Input layer is required. Select one of the layers from input section."
            )
        if graph_has_savel is False:
            raise GraphError(
                "Output layer is required. Select one of the layers from output section to save results."
            )
        if len(self.layers) < 2:
            raise GraphError(
                "You need at least one input and one output layer to run the pipeline."
            )
        self.check_connections()

    def modifies_data(self):
        for layer in self.layers:
            if layer.modifies_data():
                return True
        return False

    def get_input_project_metas(self):
        data_layers_idxs = [idx for idx, layer in enumerate(self.layers) if layer.type == "data"]
        input_project_metas = {}
        for idx in data_layers_idxs:
            data_layer = self.layers[idx]
            for src in data_layer.srcs:
                project_name = src.split("/")[0]
                if project_name not in input_project_metas:
                    input_project_metas[project_name] = get_project_meta(
                        get_project_by_name(project_name).id
                    )
        return input_project_metas

    def preprocess(self):
        for layer in self.layers:
            layer.preprocess()

    def postprocess(self):
        for layer in self.layers:
            layer.postprocess()

    def may_require_items(self):
        for l in self.layers:
            if l.requires_item():
                return True
        return False

    def check_connections(self, indx=-1):
        if indx == -1:
            for i in range(len(self.layers)):
                if self.layers[i].type == "data":
                    for layer_ in self.layers:
                        layer_.color = "not visited"
                    self.src_check_mappings = []
                    self.check_connections(i)
        else:
            color = self.layers[indx].color
            if color == "visiting":
                raise GraphError("Loop in layers structure.")
            if color == "visited":
                return
            self.layers[indx].color = "visiting"
            for next_layer_indx in self.get_next_layer_indxs(indx):
                self.check_connections(next_layer_indx)
            self.layers[indx].color = "visited"

    def get_next_layer_indxs(self, indx, branch=-1, layers_idx_whitelist=None):
        #:param indx:
        #:param branch: specify when calling while processing images, do not specify when calling before processing images
        #:return:

        if indx >= len(self.layers):
            raise RuntimeError("Invalid layer index.")
        if branch == -1:  # check class mappings
            if hasattr(self.layers[indx], "src_check_mappings"):
                for cls in self.layers[indx].src_check_mappings:
                    self.src_check_mappings.append((indx, cls))
            if hasattr(self.layers[indx], "dst_check_mappings"):
                for i, cls in self.src_check_mappings:
                    for l_name, l in self.layers[indx].dst_check_mappings.items():
                        if cls not in l:
                            raise RuntimeError(
                                'No mapping for class "{}" declared in layer "{}" in "{}" mapping in layer "{}"'.format(
                                    cls,
                                    self.layers[i].description(),
                                    l_name,
                                    self.layers[indx].description(),
                                )
                            )

        if self.layers[indx].type == "save":
            return []

        if branch == -1:
            dsts = self.layers[indx].dsts
        else:
            dsts = [self.layers[indx].dsts[branch]]
        dsts = list(set(dsts) - {Layer.null})

        result = []
        for dst in dsts:
            for i, layer_ in enumerate(self.layers):
                if dst in layer_.srcs:
                    if layers_idx_whitelist is None or i in layers_idx_whitelist:
                        result.append(i)
        return result

    def reset_existing_names(self):
        self.existing_names = {}

    def start(self, data_el, layers_idx_whitelist=None):
        img_pr_name = data_el[0].get_pr_name()
        img_ds_name = data_el[0].get_ds_name()

        start_layer_indxs = set()
        for idx, layer in enumerate(self.layers):
            if layer.type != "data":
                continue
            if layer.project_name == img_pr_name and (
                "*" in layer.dataset_names or img_ds_name in layer.dataset_names
            ):
                start_layer_indxs.add(idx)
        if len(start_layer_indxs) == 0:
            raise RuntimeError("Can not find data layer for the image: {}".format(data_el))

        for start_layer_indx in start_layer_indxs:
            output_generator = self.process(
                start_layer_indx, data_el, layers_idx_whitelist=layers_idx_whitelist
            )
            for output in output_generator:
                yield output

    def start_iterate(self, data_el, layer_idx: int = None, layers_idx_whitelist: list = None):
        img_pr_name = data_el[0].get_pr_name()
        img_ds_name = data_el[0].get_ds_name()

        if layer_idx is not None:
            start_layer_indxs = [layer_idx]
        else:
            start_layer_indxs = set()
            for idx, layer in enumerate(self.layers):
                if layers_idx_whitelist is not None and idx not in layers_idx_whitelist:
                    continue
                if layer.type != "data":
                    continue
                if layer.project_name == img_pr_name and (
                    "*" in layer.dataset_names or img_ds_name in layer.dataset_names
                ):
                    start_layer_indxs.add(idx)
            if len(start_layer_indxs) == 0:
                raise RuntimeError("Can not find data layer for the image: {}".format(data_el))

        for start_layer_indx in start_layer_indxs:
            output_generator = self.process_iterate(
                start_layer_indx, data_el, layers_idx_whitelist=layers_idx_whitelist
            )
            for output in output_generator:
                yield output

    def push(self, indx, data_el, branch, layers_idx_whitelist=None):
        next_layer_indxs = self.get_next_layer_indxs(
            indx, branch=branch, layers_idx_whitelist=layers_idx_whitelist
        )
        for next_layer_indx in next_layer_indxs:
            for x in self.process(
                next_layer_indx, data_el, layers_idx_whitelist=layers_idx_whitelist
            ):
                yield x

    def push_iterate(self, indx, data_el, branch, layers_idx_whitelist=None):
        next_layer_indxs = self.get_next_layer_indxs(
            indx, branch=branch, layers_idx_whitelist=layers_idx_whitelist
        )
        for next_layer_indx in next_layer_indxs:
            for x in self.process_iterate(
                next_layer_indx, data_el, layers_idx_whitelist=layers_idx_whitelist
            ):
                yield x

    def process(self, indx, data_el, layers_idx_whitelist=None):
        layer = self.layers[indx]
        for layer_output in layer.process_timed(data_el):
            if layer_output is None:
                raise RuntimeError("Layer_output ({}) is None.".format(layer))

            if len(layer_output) == 3:
                new_data_el = layer_output[:2]
                branch = layer_output[-1]
            elif len(layer_output) == 2:
                new_data_el = layer_output
                branch = 0
            elif len(layer_output) == 1:
                yield layer_output
                continue
            else:
                raise RuntimeError(
                    "Wrong number of items in layer output ({}). Got {} items.".format(
                        layer, len(layer_output)
                    )
                )
            for x in self.push(
                indx, new_data_el, branch, layers_idx_whitelist=layers_idx_whitelist
            ):
                yield x

    def process_iterate(self, indx, data_el, layers_idx_whitelist=None):
        layer = self.layers[indx]
        try:
            layer.validate()
        except CustomException as e:
            e.extra["layer_config"] = layer.config
            raise e
        except:
            raise
        for layer_output in layer.process_timed(data_el):
            if layer_output is None:
                raise RuntimeError("Layer_output ({}) is None.".format(layer))

            if len(layer_output) == 3:
                new_data_el = layer_output[:2]
                branch = layer_output[-1]
            elif len(layer_output) == 2:
                new_data_el = layer_output
                branch = 0
            elif len(layer_output) == 1:
                yield layer_output, indx
                continue
            else:
                raise RuntimeError(
                    "Wrong number of items in layer output ({}). Got {} items.".format(
                        layer, len(layer_output)
                    )
                )
            yield layer_output, indx
            for x in self.push_iterate(
                indx, new_data_el, branch, layers_idx_whitelist=layers_idx_whitelist
            ):
                yield x

    ############################################################################################################
    # Process classes begin
    ############################################################################################################
    def get_total_elements(self):
        total = 0
        data_layers_idxs = [idx for idx, layer in enumerate(self.layers) if layer.type == "data"]
        datasets = []
        added = set()
        for data_layer_idx in data_layers_idxs:
            data_layer = self.layers[data_layer_idx]
            for src in data_layer.srcs:
                project_name, dataset_name = src.split("/")
                project = get_project_by_name(project_name)
                if dataset_name == "*":
                    for dataset in get_all_datasets(project.id):
                        if dataset.id not in added:
                            datasets.append(dataset)
                            added.add(dataset.id)
                else:
                    dataset = get_dataset_by_name(dataset_name, project.id)
                    if dataset.id not in added:
                        datasets.append(dataset)
                        added.add(dataset.id)
        for dataset in datasets:
            total += dataset.items_count
        return total

    def get_elements_generator(self):
        require_items = self.may_require_items()
        data_layers_idxs = [idx for idx, layer in enumerate(self.layers) if layer.type == "data"]
        project_datasets = {}
        added = set()
        for data_layer_idx in data_layers_idxs:
            data_layer = self.layers[data_layer_idx]
            for src in data_layer.srcs:
                project_name, dataset_name = src.split("/")
                project = get_project_by_name(project_name)
                if dataset_name == "*":
                    project_datasets.setdefault(project.id, [])
                    for dataset in get_all_datasets(project.id):
                        if dataset.id not in added:
                            project_datasets[project.id].append(dataset.id)
                            added.add(dataset.id)
                else:
                    dataset = get_dataset_by_name(dataset_name, project.id)
                    if dataset.id not in added:
                        project_datasets.setdefault(project.id, []).append(dataset.id)
                        added.add(dataset.id)
        for project_id, dataset_ids in project_datasets.items():
            project_meta = get_project_meta(project_id)
            project_info = get_project_by_id(project_id)
            for dataset_id in dataset_ids:
                dataset_info = get_dataset_by_id(dataset_id)
                if self.modality == "images":
                    for batch in g.api.image.get_list_generator(
                        dataset_id=dataset_id, batch_size=50
                    ):
                        for img_info in batch:
                            img_data = np.zeros(
                                (img_info.height, img_info.width, 3), dtype=np.uint8
                            )
                            if require_items:
                                img_data = g.api.image.download_np(img_info.id)
                            img_desc = ImageDescriptor(
                                LegacyProjectItem(
                                    project_name=project_info.name,
                                    ds_name=dataset_info.name,
                                    item_name=".".join(img_info.name.split(".")[:-1]),
                                    item_info=img_info,
                                    ia_data={"item_ext": "." + img_info.ext},
                                    item_path="",
                                    ann_path="",
                                ),
                                False,
                            )
                            img_desc.update_item(img_data)
                            ann = Annotation.from_json(
                                g.api.annotation.download(img_info.id).annotation, project_meta
                            )
                            data_el = (img_desc, ann)
                            yield data_el
                elif self.modality == "videos":
                    for batch in g.api.video.get_list_generator(
                        dataset_id=dataset_id, batch_size=1
                    ):
                        for vid_info in batch:
                            vid_ext = get_file_ext(vid_info.name)
                            vid_desc = VideoDescriptor(
                                LegacyProjectItem(
                                    project_name=project_info.name,
                                    ds_name=dataset_info.name,
                                    item_name=".".join(vid_info.name.split(".")[:-1]),
                                    item_info=vid_info,
                                    ia_data={"item_ext": vid_ext},
                                    item_path="",
                                    ann_path="",
                                ),
                                False,
                            )

                            video_path = os.path.join(g.DATA_DIR, vid_info.name)
                            g.api.video.download_path(vid_info.id, video_path)
                            vid_desc.update_item(video_path)
                            ann_json = g.api.video.annotation.download(vid_info.id)
                            ann = VideoAnnotation.from_json(
                                ann_json,
                                project_meta,
                                KeyIdMap(),
                            )
                            data_el = (vid_desc, ann)
                            yield data_el

    def get_result_project_meta(self):
        return self._output_meta

    def calc_metas(self):
        cur_level_layers = {layer for layer in self.layers if layer.type == "data"}
        datalevel_metas = {}
        for data_layer in cur_level_layers:
            try:
                input_meta = data_layer.in_project_meta
            except AttributeError:
                input_meta = ProjectMeta()
            except KeyError:
                input_meta = ProjectMeta()
            for src in data_layer.srcs:
                datalevel_metas[src] = input_meta

        def get_dest_layers(the_layer):
            return [
                dest_layer
                for dest_layer in self.layers
                if len(set(the_layer.dsts) & set(dest_layer.srcs)) > 0
            ]

        def layer_input_metas_are_calculated(the_layer):
            return all((x in datalevel_metas for x in the_layer.srcs))

        processed_layers = set()
        while len(cur_level_layers) != 0:
            next_level_layers = set()

            for cur_layer in cur_level_layers:
                processed_layers.add(cur_layer)
                # TODO no need for dict here?
                cur_layer_input_metas = {src: datalevel_metas[src] for src in cur_layer.srcs}
                try:
                    cur_layer_res_meta = cur_layer.make_output_meta(cur_layer_input_metas)
                except CreateMetaError as e:
                    e.extra["layer_config"] = cur_layer.config
                    raise e

                for dst in cur_layer.dsts:
                    datalevel_metas[dst] = cur_layer_res_meta

                dest_layers = get_dest_layers(cur_layer)
                for next_candidate in dest_layers:
                    if layer_input_metas_are_calculated(next_candidate):
                        next_level_layers.update([next_candidate])

            cur_level_layers = next_level_layers

        # if set(processed_layers) != set(self.layers):
        #     raise RuntimeError("Graph has several connected components. Only one is allowed.")

    def calc_metas_iter(self):
        cur_level_layers = {layer for layer in self.layers if layer.type == "data"}
        datalevel_metas = {}
        for data_layer in cur_level_layers:
            try:
                input_meta = data_layer.in_project_meta
            except AttributeError:
                input_meta = ProjectMeta()
            except KeyError:
                input_meta = ProjectMeta()
            for src in data_layer.srcs:
                datalevel_metas[src] = input_meta

        def get_dest_layers(the_layer):
            return [
                dest_layer
                for dest_layer in self.layers
                if len(set(the_layer.dsts) & set(dest_layer.srcs)) > 0
            ]

        def layer_input_metas_are_calculated(the_layer):
            return all((x in datalevel_metas for x in the_layer.srcs))

        processed_layers = set()
        while len(cur_level_layers) != 0:
            next_level_layers = set()

            for cur_layer in cur_level_layers:
                processed_layers.add(cur_layer)
                # TODO no need for dict here?
                cur_layer_input_metas = {src: datalevel_metas[src] for src in cur_layer.srcs}
                cur_layer_res_meta = cur_layer.make_output_meta(cur_layer_input_metas)

                for dst in cur_layer.dsts:
                    datalevel_metas[dst] = cur_layer_res_meta

                yield cur_layer_res_meta, cur_layer

                dest_layers = get_dest_layers(cur_layer)
                for next_candidate in dest_layers:
                    if layer_input_metas_are_calculated(next_candidate):
                        next_level_layers.update([next_candidate])

            cur_level_layers = next_level_layers


############################################################################################################
# Process classes end
############################################################################################################
