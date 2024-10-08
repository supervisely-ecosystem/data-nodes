# coding: utf-8

from typing import Tuple, Union, List

from supervisely.io.fs import get_file_name
from supervisely import (
    Annotation,
    VideoAnnotation,
    KeyIdMap,
    ProjectMeta,
    DatasetInfo,
    TagValueType,
    TagMetaCollection,
)
import supervisely.io.fs as sly_fs
import supervisely.io.json as sly_json
from src.compute.dtl_utils.item_descriptor import ImageDescriptor, VideoDescriptor
from src.compute.Layer import Layer
from src.exceptions import GraphError
import src.globals as g
from supervisely.io.fs import get_file_ext


class AddToExistingProjectLayer(Layer):
    action = "add_to_existing_project"
    legacy_action = "existing_project"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["dataset_option"],
                "properties": {
                    "dataset_option": {
                        "type": "string",
                        "enum": ["new", "existing", "keep"],
                    },
                    "dataset_name": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "dataset_id": {"oneOf": [{"type": "integer"}, {"type": "null"}]},
                    "merge_different_meta": {"type": "boolean"},
                },
            },
        },
    }

    def __init__(self, config, output_folder, net):
        Layer.__init__(self, config, net=net)
        self.sly_project_info = None
        self.ds_map = {}

    def validate(self):
        if self.net.preview_mode:
            return

        settings = self.settings

        if settings["dataset_option"] == "new":
            if settings["dataset_name"] is None or settings["dataset_name"] == "":
                raise GraphError("Dataset name is empty")

        if settings["dataset_option"] == "existing":
            if settings["dataset_id"] is None:
                raise GraphError("Dataset is not selected")

        super().validate()

    def validate_dest_connections(self):
        if len(self.dsts) != 1:
            raise GraphError("Destination ID in '{}' layer is empty!".format(self.action))
        try:
            if not isinstance(self.dsts[0], int):
                self.dsts[0] = int(self.dsts[0])
        except Exception as e:
            raise GraphError(error=e)

    def preprocess(self):
        if self.net.preview_mode:
            return
        if self.output_meta is None:
            raise GraphError(
                "Output meta is not set. Check that node is connected", extra={"layer": self.action}
            )
        if len(self.dsts) == 0:
            raise GraphError(
                "Select destination project or dataset in the 'Add to Existing Project' layer"
            )

        dst = self.dsts[0]
        self.out_project_id = dst
        if self.out_project_id is None:
            raise GraphError("Project is not selected")

        self.sly_project_info = g.api.project.get_info_by_id(self.out_project_id)
        if self.sly_project_info is None:
            raise GraphError("Selected project does not exist.")

        dst_meta = ProjectMeta.from_json(g.api.project.get_meta(self.out_project_id))

        if self.output_meta != dst_meta:
            if self.settings["merge_different_meta"]:
                updated_tag_metas = []
                for tm in self.output_meta.tag_metas:
                    if tm.value_type == TagValueType.ONEOF_STRING:
                        dst_tm = dst_meta.get_tag_meta(tm.name)
                        if dst_tm is not None:
                            if dst_tm.value_type != TagValueType.ONEOF_STRING:
                                raise GraphError(
                                    f"Tag '{tm.name}' has different value type in destination project"
                                )
                            tm = tm.clone(
                                possible_values=list(
                                    set(tm.possible_values).union(set(dst_tm.possible_values))
                                )
                            )
                    updated_tag_metas.append(tm)
                self.output_meta = self.output_meta.clone(
                    tag_metas=TagMetaCollection(updated_tag_metas)
                )

                try:
                    self.output_meta = ProjectMeta.merge(dst_meta, self.output_meta)
                    g.api.project.update_meta(self.out_project_id, self.output_meta)
                except Exception as e:
                    raise GraphError(f"Failed to merge meta: {e}")
            else:
                raise GraphError("The meta update has not been confirmed")

        if self.settings["dataset_option"] == "existing":
            if self.net.modality == "images":
                entities_info_list = g.api.image.get_list(self.settings["dataset_id"])
            elif self.net.modality == "videos":
                entities_info_list = g.api.video.get_list(self.settings["dataset_id"])
            dataset_info = self.get_dataset_by_id(self.settings["dataset_id"])
            existing_names = set(get_file_name(info.name) for info in entities_info_list)

            existing_dataset = self.existing_names.get(
                f"{self.sly_project_info.name}/{dataset_info.name}"
            )
            if existing_dataset is None:
                self.existing_names[f"{self.sly_project_info.name}/{dataset_info.name}"] = (
                    existing_names
                )
            else:
                self.existing_names[f"{self.sly_project_info.name}/{dataset_info.name}"].update(
                    existing_names
                )

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
        # @TODO: create project with change_name_if_conflict=True
        parent_id = self.sly_project_info.id
        for parent_name in ds_parents:
            if parent_id == self.sly_project_info.id:
                # parent_ds_info = g.api.dataset.get_or_create(self.sly_project_info.id, parent_name)
                parent_ds_info = g.api.dataset.get_info_by_name(
                    self.sly_project_info.id, parent_name
                )
                if parent_ds_info is None:
                    parent_ds_info = g.api.dataset.create(
                        self.sly_project_info.id, parent_name, change_name_if_conflict=True
                    )
            else:
                # parent_ds_info = g.api.dataset.get_or_create(self.sly_project_info.id, parent_name, parent_id=parent_id)
                parent_ds_info = g.api.dataset.get_info_by_name(
                    self.sly_project_info.id, parent_name, parent_id=parent_id
                )
                if parent_ds_info is None:
                    parent_ds_info = g.api.dataset.create(
                        self.sly_project_info.id,
                        parent_name,
                        parent_id=parent_id,
                        change_name_if_conflict=True,
                    )
            parent_id = parent_ds_info.id

        dataset_info = g.api.dataset.get_info_by_name(
            self.sly_project_info.id, parent_name, parent_id=parent_id
        )
        if dataset_info is None:

            def get_free_name(name):
                res_title = name
                suffix = 1
                while g.api.dataset.exists(
                    self.sly_project_info.id, res_title, parent_id=parent_id
                ):
                    res_title = "{}_{:03d}".format(name, suffix)
                    suffix += 1
                return res_title

            dataset_name = get_free_name(dataset_name)
            dataset_info = g.api.dataset.create(
                self.sly_project_info.id,
                dataset_name,
                parent_id=parent_id,
                change_name_if_conflict=True,
            )
        return dataset_info

    def get_or_create_dataset(self, dataset_name, ds_parents=None):
        if ds_parents is None:
            if dataset_name not in self.ds_map:
                dataset_info = g.api.dataset.create(
                    self.out_project_id, dataset_name, change_name_if_conflict=True
                )
                self.ds_map[dataset_name] = dataset_info
                return dataset_info
            else:
                return self.ds_map[dataset_name]
        else:
            if dataset_name not in self.ds_map:
                dataset_info = self.get_or_create_nested_dataset(dataset_name, ds_parents)
                self.ds_map[dataset_name] = dataset_info
                return dataset_info
            else:
                return self.ds_map[dataset_name]

    def get_dataset_by_id(self, dataset_id) -> DatasetInfo:
        return self.ds_map.setdefault(dataset_id, g.api.dataset.get_info_by_id(dataset_id))

    def process_batch(
        self,
        data_els: List[
            Tuple[Union[ImageDescriptor, VideoDescriptor], Union[Annotation, VideoAnnotation]]
        ],
    ):
        if not self.net.preview_mode:
            item_descs, anns = zip(*data_els)

            ds_item_map = None
            dataset_option = self.settings["dataset_option"]
            if not self.net.preview_mode:
                if dataset_option == "new":
                    dataset_name = self.settings["dataset_name"]
                    dataset_info = self.get_or_create_dataset(dataset_name)
                elif dataset_option == "existing":
                    dataset_info = self.get_dataset_by_id(self.settings["dataset_id"])
                    dataset_name = dataset_info.name
                else:
                    ds_item_map = {}
                    for item_desc, ann in zip(item_descs, anns):
                        dataset_name = item_desc.get_res_ds_name()
                        if dataset_name not in ds_item_map:
                            ds_item_map[dataset_name] = []
                        ds_item_map[dataset_name].append((item_desc, ann))

                if ds_item_map is None:
                    out_item_names = [
                        self.get_free_name(
                            item_desc.get_item_name(), dataset_name, self.sly_project_info.name
                        )
                        + get_file_ext(item_desc.info.item_info.name)
                        for item_desc in item_descs
                    ]
                    if self.net.modality == "images":
                        if self.net.may_require_items():
                            image_info = g.api.image.upload_nps(
                                dataset_info.id,
                                out_item_names,
                                [item_desc.read_image() for item_desc in item_descs],
                            )
                        else:
                            image_info = g.api.image.upload_ids(
                                dataset_info.id,
                                out_item_names,
                                [item_desc.info.item_info.id for item_desc in item_descs],
                            )

                        new_item_ids = [image_info.id for image_info in image_info]
                        g.api.annotation.upload_anns(new_item_ids, anns)
                    elif self.net.modality == "videos":
                        video_info = g.api.video.upload_paths(
                            dataset_info.id, out_item_names, item_desc.item_data
                        )
                        ann_paths = [f"{item_desc.item_data}.json" for item_desc in item_descs]
                        for ann_path in ann_paths:
                            if not sly_fs.file_exists(ann_path):
                                ann_json = ann.to_json(KeyIdMap())
                                sly_json.dump_json_file(ann_json, ann_path)
                            g.api.video.annotation.upload_paths(
                                [video_info.id], [ann_path], self.output_meta
                            )

                else:
                    for ds_name in ds_item_map:
                        orig_ds_info = ds_item_map[ds_name][0][
                            0
                        ].info.ds_info  # @TODO: not safe, fix later
                        ds_parents = self.get_ds_parents(orig_ds_info)
                        dataset_info = self.get_or_create_dataset(ds_name, ds_parents)
                        dataset_name = dataset_info.name

                        out_item_names = [
                            self.get_free_name(
                                item_desc.get_item_name(), dataset_name, self.sly_project_info.name
                            )
                            + get_file_ext(item_desc.info.item_info.name)
                            for item_desc, _ in ds_item_map[ds_name]
                        ]

                        if self.net.modality == "images":
                            if self.net.may_require_items():
                                image_nps = [
                                    item_desc.read_image() for item_desc, _ in ds_item_map[ds_name]
                                ]
                                image_info = g.api.image.upload_nps(
                                    dataset_info.id, out_item_names, image_nps
                                )
                            else:
                                item_ids = [
                                    item_desc.info.item_info.id
                                    for item_desc, _ in ds_item_map[ds_name]
                                ]
                                image_info = g.api.image.upload_ids(
                                    dataset_info.id, out_item_names, item_ids
                                )
                            anns = [ann for _, ann in ds_item_map[ds_name]]
                            upload_ids = [info.id for info in image_info]
                            g.api.annotation.upload_anns(upload_ids, anns)
                        elif self.net.modality == "videos":
                            video_datas = [
                                item_desc.item_data for item_desc, _ in ds_item_map[dataset_name]
                            ]
                            video_info = g.api.video.upload_paths(
                                dataset_info.id, out_item_names, video_datas
                            )

                            ann_paths = [
                                f"{item_desc.item_data}.json"
                                for item_desc, _ in ds_item_map[dataset_name]
                            ]
                            for ann_path in ann_paths:
                                if not sly_fs.file_exists(ann_path):
                                    ann_json = ann.to_json(KeyIdMap())
                                    sly_json.dump_json_file(ann_json, ann_path)
                                g.api.video.annotation.upload_paths(
                                    [video_info.id], [ann_path], self.output_meta
                                )

        yield data_els

    def has_batch_processing(self) -> bool:
        return True

    def postprocess(self):
        self.postprocess_cb()
