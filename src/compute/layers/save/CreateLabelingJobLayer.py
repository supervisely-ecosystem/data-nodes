# coding: utf-8

from typing import Tuple, Union, List
from collections import defaultdict
from supervisely import Annotation, VideoAnnotation, KeyIdMap, ProjectMeta
import supervisely.io.fs as sly_fs
import supervisely.io.json as sly_json
from src.compute.dtl_utils.item_descriptor import ImageDescriptor, VideoDescriptor
from src.compute.Layer import Layer
from src.exceptions import BadSettingsError
import src.globals as g


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


def _filter_meta(dataset_id: int, classes_to_label: List[str], tags_to_label: List[str]):
    dataset_info = g.api.dataset.get_info_by_id(dataset_id)
    project_id = dataset_info.project_id
    project_meta_json = g.api.project.get_meta(project_id)
    project_meta = ProjectMeta.from_json(project_meta_json)
    obj_classes_names = [obj_class.name for obj_class in project_meta.obj_classes]
    filtered_classes_to_label = []
    for obj_class_name in classes_to_label:
        if obj_class_name in obj_classes_names:
            filtered_classes_to_label.append(obj_class_name)
    tag_metas_names = [tag_meta.name for tag_meta in project_meta.tag_metas]
    filtered_tags_to_label = []
    for tag_meta_name in tags_to_label:
        if tag_meta_name in tag_metas_names:
            filtered_tags_to_label.append(tag_meta_name)
    return filtered_classes_to_label, filtered_tags_to_label


class CreateLabelingJobLayer(Layer):
    action = "create_labeling_job"
    legacy_action = "labeling_job"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": [
                    "job_name",
                    "description",
                    "readme",
                    "user_ids",
                    "reviewer_id",
                    "classes_to_label",
                    "tags_to_label",
                    "create_new_project",
                    "project_name",
                    "dataset_name",
                    "keep_original_ds",
                ],
                "properties": {
                    # description
                    "job_name": {"type": "string"},
                    "description": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "readme": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    # members
                    "user_ids": {"type": "array", "items": {"type": "integer"}},
                    "reviewer_id": {"type": "integer"},
                    # classes
                    "classes_to_label": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}},
                        ]
                    },
                    # tags
                    "tags_to_label": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}},
                        ]
                    },
                    # output
                    "create_new_project": {"type": "boolean"},
                    "project_name": {"type": "string"},
                    "dataset_name": {"oneOf": [{"type": "string"}, {"type": "null"}]},
                    "keep_original_ds": {"type": "boolean"},
                },
            },
        },
    }

    def __init__(self, config, output_folder, net):
        Layer.__init__(self, config, net=net)
        self.output_folder = output_folder
        self.sly_project_info = None
        self._labeling_job_map = defaultdict(list)  # {"dataset_id": ["images_ids"]}
        self.created_labeling_jobs = []

    def validate(self):
        settings = self.settings

        job_name = settings.get("job_name", "")
        if job_name == "" or job_name is None:
            raise BadSettingsError("Labeling Job name is not set")
        elif len(job_name) > 256:
            raise BadSettingsError("Labeling Job name is too long")

        if settings["reviewer_id"] is None:
            raise BadSettingsError("Reviewer is not set")

        if settings["user_ids"] is None or len(settings["user_ids"]) == 0:
            raise BadSettingsError("Labelers are not set")

        if (settings["classes_to_label"] is None or len(settings["classes_to_label"]) == 0) and (
            settings["tags_to_label"] is None or len(settings["tags_to_label"]) == 0
        ):
            raise BadSettingsError("Set at least one class or tag to label")

        if settings["create_new_project"]:
            if settings["project_name"] is None or settings["project_name"] == "":
                raise BadSettingsError("Project name is not set")

            if len(settings["project_name"]) > 256:
                raise BadSettingsError("Project name is too long")

            if not settings["keep_original_ds"]:
                if settings["dataset_name"] is None or settings["dataset_name"] == "":
                    raise BadSettingsError(
                        "Dataset name is not set. Enter dataset name or check 'Keep original datasets structure' checkbox"
                    )

                if len(settings["dataset_name"]) > 256:
                    raise BadSettingsError("Dataset name is too long")
        super().validate()

    def validate_dest_connections(self):
        for dst in self.dsts:
            if len(dst) == 0:
                raise BadSettingsError(
                    "Destination name in '{}' layer is empty!".format(self.action)
                )

    def modifies_data(self):
        return False

    def preprocess(self):
        if self.net.preview_mode:
            return
        if self.output_meta is None:
            raise BadSettingsError(
                "Output meta is not set. Check that node is connected", extra={"layer": self.action}
            )
        if len(self.dsts) == 0 and self.settings["create_new_project"]:
            raise BadSettingsError(
                "Enter title for the Labeling Job in the 'Create Labeling Job' layer"
            )
            # raise GraphError(
            #     "Destination is not set", extra={"layer_config": self.config, "layer": self.action}
            # )

        if self.settings["create_new_project"]:
            dst = self.dsts[0]
            self.out_project_name = dst

            self.sly_project_info = g.api.project.create(
                g.WORKSPACE_ID,
                self.settings["project_name"],
                type=self.net.modality,
                change_name_if_conflict=True,
            )
            g.api.project.update_meta(self.sly_project_info.id, self.output_meta)

            custom_data = {
                "source_projects": _get_source_projects_ids_from_dtl(),
                "data-nodes": g.current_dtl_json,
            }
            g.api.project.update_custom_data(self.sly_project_info.id, custom_data)
        else:  # use input project
            project_id = _get_source_projects_ids_from_dtl()[0]
            src_project_info = g.api.project.get_info_by_id(project_id)
            dst = src_project_info.name
            self.out_project_name = dst
            self.sly_project_info = g.api.project.get_info_by_id(project_id, self.net.modality)
            # need custom data update?

    def get_or_create_dataset(self, dataset_name):
        if not g.api.dataset.exists(self.sly_project_info.id, dataset_name):
            return g.api.dataset.create(self.sly_project_info.id, dataset_name)
        else:
            return g.api.dataset.get_info_by_name(self.sly_project_info.id, dataset_name)

    def process(
        self,
        data_el: Tuple[Union[ImageDescriptor, VideoDescriptor], Union[Annotation, VideoAnnotation]],
    ):
        item_desc, ann = data_el

        if not self.net.preview_mode:
            if not self.settings["keep_original_ds"]:
                dataset_name = self.settings["dataset_name"]
            else:
                dataset_name = item_desc.get_res_ds_name()
            out_item_name = (
                self.get_free_name(item_desc.get_item_name(), dataset_name, self.out_project_name)
                + item_desc.get_item_ext()
            )
            if self.sly_project_info is not None:
                if self.settings["create_new_project"]:
                    dataset_info = self.get_or_create_dataset(dataset_name)
                    if self.net.modality == "images":
                        if self.net.may_require_items():
                            item_info = g.api.image.upload_np(
                                dataset_info.id, out_item_name, item_desc.read_image()
                            )
                        else:
                            item_info = g.api.image.upload_id(
                                dataset_info.id, out_item_name, item_desc.info.item_info.id
                            )
                        g.api.annotation.upload_ann(item_info.id, ann)
                    elif self.net.modality == "videos":
                        item_info = g.api.video.upload_path(
                            dataset_info.id, out_item_name, item_desc.item_data
                        )
                        ann_path = f"{item_desc.item_data}.json"
                        if not sly_fs.file_exists(ann_path):
                            ann_json = ann.to_json(KeyIdMap())
                            sly_json.dump_json_file(ann_json, ann_path)
                        g.api.video.annotation.upload_paths(
                            [item_info.id], [ann_path], self.output_meta
                        )
                    self._labeling_job_map[dataset_info.id].append(item_info.id)
                else:
                    self._labeling_job_map[item_desc.info.item_info.dataset_id].append(
                        item_desc.info.item_info.id
                    )

        yield ([item_desc, ann])

    def postprocess(self):
        name = self.settings.get("job_name", None)
        description = self.settings.get("description", None)
        readme = self.settings.get("readme", None)

        user_ids = self.settings.get("user_ids", None)
        reviewer_id = self.settings.get("reviewer_id", None)
        classes_to_label = self.settings.get("classes_to_label", None)
        if classes_to_label == "default":
            classes_to_label = [obj_class.name for obj_class in self.output_meta.obj_classes]

        tags_to_label = self.settings.get("tags_to_label", None)
        if tags_to_label == "default":
            tags_to_label = [tag_meta.name for tag_meta in self.output_meta.tag_metas]

        dataset_ids = self._labeling_job_map.keys()
        for dataset_id in dataset_ids:
            filtered_classes_to_label, filtered_tags_to_label = _filter_meta(
                dataset_id, classes_to_label, tags_to_label
            )
            items_ids = self._labeling_job_map[dataset_id]
            created_lj_infos = g.api.labeling_job.create(
                name=name,
                dataset_id=dataset_id,
                user_ids=user_ids,
                readme=readme,
                description=description,
                classes_to_label=filtered_classes_to_label,
                objects_limit_per_image=None,
                tags_to_label=filtered_tags_to_label,
                tags_limit_per_image=None,
                include_images_with_tags=None,
                exclude_images_with_tags=None,
                images_range=None,
                reviewer_id=reviewer_id,
                images_ids=items_ids,
            )
            self.created_labeling_jobs.extend(created_lj_infos)
