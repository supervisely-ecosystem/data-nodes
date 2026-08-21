# coding: utf-8

from typing import Tuple, List
from collections import defaultdict
import supervisely as sly
from supervisely import (
    Annotation,
    ProjectMeta,
    DatasetInfo,
    TagValueType,
    TagMetaCollection,
    ProjectInfo,
    ImageInfo,
)
from supervisely.api.app_api import SessionInfo
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from src.compute.Layer import Layer
from src.compute.tags_utils import is_duplicate_tags_allowed, remove_duplicate_tags
from src.exceptions import GraphError
import src.globals as g
from supervisely.io.fs import get_file_name


def _get_source_projects_ids_from_dtl():
    source_project_id_ds_map = {}
    for action in g.current_dtl_json:
        if action["action"] in ("images_project", "videos_project", "input_labeling_job"):
            if len(action["src"]) == 0:
                continue
            project_name = action["src"][0].split("/")[0]
            project = g.api.project.get_info_by_name(g.WORKSPACE_ID, project_name)

            project_map = source_project_id_ds_map.get(project.id)
            if project_map is None:
                source_project_id_ds_map[project.id] = []

            ds_name = action["src"][0].split("/")[1]
            if ds_name == "*":
                datasets = g.api.dataset.get_list(project.id, recursive=True)
                for ds in datasets:
                    source_project_id_ds_map[project.id].append(ds)
                continue
            else:
                for ds in action["src"]:
                    dataset_name = ds.split("/")[1]
                    dataset = g.api.dataset.get_info_by_name(project.id, dataset_name)
                    source_project_id_ds_map[project.id].append(dataset)

    return source_project_id_ds_map


def backup_destination_project(project_info: ProjectInfo) -> SessionInfo:
    app_slug = "supervisely-ecosystem/sys-clone-project"
    module_id = g.api.app.get_ecosystem_module_id(app_slug)
    module_info = g.api.app.get_ecosystem_module_info(module_id)

    agent_id = sly.env.agent_id(raise_not_found=False) or None
    agent_id = None
    module_params = module_info.get_arguments(images_project=project_info.id)
    module_params["projectName"] = f"{project_info.name}_backup"
    module_params["teamId"] = g.TEAM_ID
    module_params["workspaceId"] = g.WORKSPACE_ID
    session = g.api.app.start(
        agent_id=agent_id,
        module_id=module_id,
        workspace_id=g.WORKSPACE_ID,
        params=module_params,
        task_name="[ML Pipelines] Add labels to existing project backup",
    )
    return session


def match_properties(
    input_image: ImageInfo, destination_image: ImageInfo, strict_match: bool = False
) -> bool:
    if (destination_image.height, destination_image.width) != (
        input_image.height,
        input_image.width,
    ):
        sly.logger.warn(
            (
                f"Image: '{destination_image.name}' (ID: '{destination_image.id}') size mismatch. "
                f"Original image size: '{input_image.height}x{input_image.width}'. "
                f"Destination image size: '{destination_image.height}x{destination_image.width}'. "
                "Skipping..."
            )
        )
        return False
    if strict_match:
        if destination_image.link != input_image.link:
            sly.logger.warn(
                (
                    f"Image: '{destination_image.name}' (ID: '{destination_image.id}') link mismatch. "
                    f"Original image link: '{input_image.link}'. "
                    f"Destination image link: '{destination_image.link}'. "
                    "Skipping..."
                )
            )
            return False
        elif destination_image.hash != input_image.hash:
            sly.logger.warn(
                (
                    f"Image: '{destination_image.name}' (ID: '{destination_image.id}') hash mismatch. "
                    f"Original image hash: '{input_image.hash}'."
                    f"Destination image hash: '{destination_image.hash}'. "
                    "Skipping..."
                )
            )
            return False
    return True


def map_matching_images_by_name(input_ds_images, destination_ds_images, strict_match):
    name_to_id_map = {get_file_name(image.name): image for image in input_ds_images}
    matched_mapping = {}
    for image in destination_ds_images:
        image_name = get_file_name(image.name)
        if image_name in name_to_id_map and match_properties(
            name_to_id_map[image_name], image, strict_match=strict_match
        ):
            matched_mapping[name_to_id_map[image_name].id] = image.id
    return matched_mapping


class CopyAnnotationsLayer(Layer):
    action = "copy_annotations"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": [
                    "project_id",
                    "dataset_ids",
                    "add_option",
                    "backup_destination_project",
                ],
                "properties": {
                    "project_id": {"oneOf": [{"type": "integer"}, {"type": "null"}]},
                    "dataset_ids": {
                        "oneOf": [{"type": "array", "items": {"type": "integer"}}, {"type": "null"}]
                    },
                    "add_option": {
                        "type": "string",
                        "enum": ["merge", "replace", "keep"],
                    },
                    "strict_match": {"type": "boolean"},
                    "backup_destination_project": {"type": "boolean"},
                },
            },
        },
    }

    def __init__(self, config, output_folder, net):
        Layer.__init__(self, config, net=net)
        self.sly_project_info = None
        self.ds_map = {}
        self.allow_duplicate_tags = False

    def validate(self):
        if self.net.preview_mode:
            return

        settings = self.settings

        if settings["project_id"] is None:
            raise GraphError(
                "Destination project is not selected in the 'Add labels to existing project' layer"
            )

        if settings["dataset_ids"] is None or len(settings["dataset_ids"]) == 0:
            raise GraphError(
                "Destination dataset is not selected in the 'Add labels to existing project' layer"
            )

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
                "Destination is not set", extra={"layer_config": self.config, "layer": self.action}
            )

        dst = self.dsts[0]
        self.out_project_id = dst
        if self.out_project_id is None:
            raise GraphError("Project is not selected")

        self.sly_project_info = g.api.project.get_info_by_id(self.out_project_id)
        if self.sly_project_info is None:
            raise ValueError("Selected project does not exist.")

        self.allow_duplicate_tags = is_duplicate_tags_allowed(self.out_project_id)

        dst_meta = ProjectMeta.from_json(g.api.project.get_meta(self.out_project_id))

        if self.settings["backup_destination_project"]:
            session = backup_destination_project(self.sly_project_info)
            sly.logger.info(
                f"Project ID: '{self.settings['project_id']}' backup is created. Task ID: '{session.task_id}'"
            )

        if self.output_meta != dst_meta:
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

        # match dataset names
        destination_dataset_infos = [
            g.api.dataset.get_info_by_id(ds_id) for ds_id in self.settings["dataset_ids"]
        ]
        destination_ds_map = {ds_info.name: ds_info for ds_info in destination_dataset_infos}
        datasets_matches = 0

        is_single_input_ds = False
        input_projects_map = _get_source_projects_ids_from_dtl()
        if len(input_projects_map) == 0:
            raise ValueError("No source projects found in the DTL")
        if len(input_projects_map) == 1:
            input_datasets_count = len(input_projects_map[list(input_projects_map.keys())[0]])
            if input_datasets_count == 1:
                is_single_input_ds = True

        for input_project_id in input_projects_map:
            datasets = input_projects_map[input_project_id]
            for dataset in datasets:
                if is_single_input_ds:
                    matching_destination_datasets = destination_dataset_infos
                else:
                    destination_ds = destination_ds_map.get(dataset.name)
                    if destination_ds is None:
                        sly.logger.warn(
                            f"Destination project does not have dataset '{dataset.name}'. Skipping..."
                        )
                        continue
                    matching_destination_datasets = [destination_ds]

                datasets_matches += len(matching_destination_datasets)

                total_ds_images = dataset.items_count
                input_images = g.api.image.get_list(dataset.id)
                strict_match = self.settings.get("strict_match", False)

                for destination_ds in matching_destination_datasets:
                    destination_images = g.api.image.get_list(destination_ds.id)
                    matched_images = map_matching_images_by_name(
                        input_images, destination_images, strict_match
                    )
                    if len(matched_images) == 0:
                        sly.logger.warn(
                            (
                                f"Dataset '{dataset.name}' (ID '{dataset.id}') has no matching images "
                                f"in destination dataset '{destination_ds.name}' (ID '{destination_ds.id}'). "
                                "Skipping..."
                            )
                        )
                        continue

                    if total_ds_images != len(matched_images):
                        sly.logger.warn(
                            (
                                f"Some images from Dataset '{dataset.name}' couldn't be matched "
                                f"in destination dataset '{destination_ds.name}'"
                            )
                        )

                    source_ds_map = self.ds_map.setdefault(dataset.id, defaultdict(list))
                    for source_image_id, destination_image_id in matched_images.items():
                        source_ds_map[source_image_id].append(
                            (destination_ds.id, destination_image_id)
                        )

        if datasets_matches == 0:
            raise ValueError(
                "No matching datasets found. Please check input and destination projects"
            )
        if len(self.ds_map) == 0:
            raise ValueError(
                "No matching images found. Please check input and destination projects"
            )

    def process_batch(self, data_els: List[Tuple[ImageDescriptor, Annotation]]):
        if self.net.preview_mode:
            yield data_els
        else:
            item_descs, anns = zip(*data_els)

            dst_item_id_map = defaultdict(list)
            dst_item_ann_map = defaultdict(list)
            for item_desc, ann in zip(item_descs, anns):
                if item_desc.item_data is None:
                    local_item_size = (
                        item_desc.info.item_info.height,
                        item_desc.info.item_info.width,
                    )
                else:
                    local_item_size = item_desc.item_data.shape[:2]
                dataset_id = item_desc.info.item_info.dataset_id
                image_id = item_desc.info.item_info.id
                destination_images = self.ds_map.get(dataset_id)
                if destination_images is not None:
                    destination_image_infos = destination_images.get(image_id, [])
                    if len(destination_image_infos) > 0:
                        original_image_size = (
                            item_desc.info.item_info.height,
                            item_desc.info.item_info.width,
                        )
                        # check image size was modified
                        if local_item_size != original_image_size:
                            sly.logger.warn(
                                (
                                    f"Image: '{item_desc.info.item_info.name}' size was modified in the pipeline. "
                                    f"Original size: '{item_desc.info.item_info.height}x{item_desc.info.item_info.width}'. "
                                    f"Modified image size: '{local_item_size[0]}x{local_item_size[1]}' "
                                    "Skipping..."
                                )
                            )
                            continue
                        else:
                            for (
                                destination_dataset_id,
                                destination_image_id,
                            ) in destination_image_infos:
                                dst_item_id_map[destination_dataset_id].append(
                                    destination_image_id
                                )
                                dst_item_ann_map[destination_dataset_id].append(ann)

            for destination_dataset_id in dst_item_id_map:
                destination_images_ids = dst_item_id_map[destination_dataset_id]
                image_anns = dst_item_ann_map[destination_dataset_id]

                add_option = self.settings["add_option"]
                if add_option == "merge":
                    ann_jsons = g.api.annotation.download_json_batch(
                        destination_dataset_id, destination_images_ids
                    )
                    destination_anns = [
                        Annotation.from_json(ann_json, self.output_meta) for ann_json in ann_jsons
                    ]
                    upload_anns = [
                        ann.merge(destination_ann)
                        for ann, destination_ann in zip(image_anns, destination_anns)
                    ]
                    upload_anns = remove_duplicate_tags(
                        upload_anns, destination_images_ids, self.allow_duplicate_tags
                    )
                    g.api.annotation.upload_anns(destination_images_ids, upload_anns)
                else:
                    upload_anns = remove_duplicate_tags(
                        image_anns, destination_images_ids, self.allow_duplicate_tags
                    )
                    g.api.annotation.upload_anns(destination_images_ids, upload_anns)

            yield tuple(zip(item_descs, anns))

    def has_batch_processing(self) -> bool:
        return True
