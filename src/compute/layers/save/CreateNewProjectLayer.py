# coding: utf-8
from typing import Tuple, Union, List

from supervisely import Annotation, VideoAnnotation, KeyIdMap, DatasetInfo
import supervisely.io.fs as sly_fs
import supervisely.io.json as sly_json
from src.compute.dtl_utils.item_descriptor import ImageDescriptor, VideoDescriptor
from src.compute.Layer import Layer
from src.compute.tags_utils import is_duplicate_tags_allowed, remove_duplicate_tags
from src.exceptions import GraphError
import src.globals as g
from supervisely.io.fs import get_file_ext


def _get_source_projects_ids_from_dtl():
    source_projects_ids = []
    for action in g.current_dtl_json:
        if action["action"] == "images_project" or action["action"] == "videos_project":
            if len(action["src"]) == 0:
                continue
            project_name = action["src"][0].split("/")[0]
            project_id = g.api.project.get_info_by_name(g.WORKSPACE_ID, project_name).id
            source_projects_ids.append(project_id)
    return source_projects_ids


class CreateNewProjectLayer(Layer):
    action = "create_new_project"
    legacy_action = "supervisely"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["project_name"],
                "properties": {
                    "project_name": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                },
            },
        },
    }

    def __init__(self, config, output_folder, net):
        Layer.__init__(self, config, net=net)
        self.output_folder = output_folder
        self.sly_project_info = None
        self.allow_duplicate_tags = False

    def validate_dest_connections(self):
        for dst in self.dsts:
            if len(dst) == 0:
                raise ValueError("Destination name in '{}' layer is empty!".format(self.action))

    def modifies_data(self):
        return False

    def preprocess(self):
        if self.net.preview_mode:
            return
        if self.output_meta is None:
            raise GraphError(
                "Output meta is not set. Check that node is connected", extra={"layer": self.action}
            )
        if len(self.dsts) == 0:
            raise GraphError(
                "Enter name for the output project to the input field in the 'Create New Project' layer"
            )

        dst = self.dsts[0]
        self.out_project_name = dst

        self.sly_project_info = g.api.project.create(
            g.WORKSPACE_ID,
            self.out_project_name,
            type=self.net.modality,
            change_name_if_conflict=True,
        )
        g.api.project.update_meta(self.sly_project_info.id, self.output_meta)
        self.allow_duplicate_tags = is_duplicate_tags_allowed(self.sly_project_info.id)

        custom_data = {
            "source_projects": _get_source_projects_ids_from_dtl(),
            "data-nodes": g.current_dtl_json,
        }
        g.api.project.update_custom_data(self.sly_project_info.id, custom_data)

    def get_ds_parents(self, dataset_info: DatasetInfo):
        if dataset_info is None:
            return None
        ds_parents = None
        for parents, dataset in g.api.dataset.tree(dataset_info.project_id):
            if dataset.name == dataset_info.name:
                ds_parents = parents
                break
        if len(ds_parents) == 0:
            return None
        else:
            return ds_parents

    def get_or_create_nested_dataset(self, dataset_name, ds_parents):
        parent_id = self.sly_project_info.id
        for parent_name in ds_parents:
            if parent_id == self.sly_project_info.id:
                parent_ds_info = g.api.dataset.get_or_create(self.sly_project_info.id, parent_name)
            else:
                parent_ds_info = g.api.dataset.get_or_create(
                    self.sly_project_info.id, parent_name, parent_id=parent_id
                )
            parent_id = parent_ds_info.id

        dataset_info = g.api.dataset.get_or_create(
            self.sly_project_info.id, dataset_name, parent_id=parent_id
        )
        return dataset_info

    def get_or_create_dataset(self, dataset_name, ds_parents=None):
        if ds_parents is None:
            if not g.api.dataset.exists(self.sly_project_info.id, dataset_name):
                return g.api.dataset.create(self.sly_project_info.id, dataset_name)
            else:
                return g.api.dataset.get_info_by_name(self.sly_project_info.id, dataset_name)
        else:
            return self.get_or_create_nested_dataset(dataset_name, ds_parents)

    def process_batch(self, data_els: List[Tuple[ImageDescriptor, Annotation]]):
        if self.net.preview_mode:
            yield data_els
        else:
            item_descs, anns = zip(*data_els)
            ds_item_map = {}
            for item_desc, ann in zip(item_descs, anns):
                dataset_name = item_desc.get_res_ds_name()
                if dataset_name not in ds_item_map:
                    ds_item_map[dataset_name] = []
                ds_item_map[dataset_name].append((item_desc, ann))

            for ds_name in ds_item_map:
                if self.sly_project_info is not None:
                    # @TODO: not safe, fix later
                    orig_ds_info = ds_item_map[ds_name][0][0].info.ds_info
                    ds_parents = self.get_ds_parents(orig_ds_info)
                    dataset_info = self.get_or_create_dataset(ds_name, ds_parents)

                    out_item_names = [
                        self.get_free_name(
                            item_desc.get_item_name(), ds_name, self.out_project_name
                        )
                        + get_file_ext(item_desc.info.item_info.name)
                        for item_desc, _ in ds_item_map[ds_name]
                    ]
                    if self.net.modality == "images":
                        if self.net.may_require_items():
                            item_infos = g.api.image.upload_nps(
                                dataset_info.id,
                                out_item_names,
                                [item_desc.read_image() for item_desc, _ in ds_item_map[ds_name]],
                            )
                        else:
                            item_infos = g.api.image.upload_ids(
                                dataset_info.id,
                                out_item_names,
                                [
                                    item_desc.info.item_info.id
                                    for item_desc, _ in ds_item_map[ds_name]
                                ],
                            )
                        upload_ids = [item_info.id for item_info in item_infos]
                        ds_anns = [ann for _, ann in ds_item_map[ds_name]]
                        upload_anns = remove_duplicate_tags(
                            ds_anns, upload_ids, self.allow_duplicate_tags
                        )
                        g.api.annotation.upload_anns(upload_ids, upload_anns)

                    elif self.net.modality == "videos":
                        item_infos = g.api.video.upload_paths(
                            dataset_info.id,
                            out_item_names,
                            [item_desc.item_data for item_desc, _ in ds_item_map[ds_name]],
                        )
                        ann_paths = [
                            f"{item_desc.item_data}.json" for item_desc, _ in ds_item_map[ds_name]
                        ]
                        for ann, ann_path, video_info in zip(
                            [ann for _, ann in ds_item_map[ds_name]], ann_paths, item_infos
                        ):
                            if not sly_fs.file_exists(ann_path):
                                ann_json = ann.to_json(KeyIdMap())
                                sly_json.dump_json_file(ann_json, ann_path)
                            g.api.video.annotation.upload_paths(
                                [video_info.id], [ann_path], self.output_meta
                            )
            yield tuple(zip(item_descs, anns))

    def has_batch_processing(self):
        return True
