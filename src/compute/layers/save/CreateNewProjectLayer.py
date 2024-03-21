# coding: utf-8

from typing import Tuple, Union

from supervisely import Annotation, VideoAnnotation, KeyIdMap
import supervisely.io.fs as sly_fs
import supervisely.io.json as sly_json
from src.compute.dtl_utils.item_descriptor import ImageDescriptor, VideoDescriptor
from src.compute.Layer import Layer
from src.exceptions import GraphError
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


class CreateNewProjectLayer(Layer):
    action = "create_new_project"
    legacy_action = "supervisely"

    layer_settings = {"required": ["settings"], "properties": {"settings": {}}}

    def __init__(self, config, output_folder, net):
        Layer.__init__(self, config, net=net)
        self.output_folder = output_folder
        self.sly_project_info = None

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

        custom_data = {
            "source_projects": _get_source_projects_ids_from_dtl(),
            "data-nodes": g.current_dtl_json,
        }
        g.api.project.update_custom_data(self.sly_project_info.id, custom_data)

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
            dataset_name = item_desc.get_res_ds_name()
            out_item_name = (
                self.get_free_name(item_desc.get_item_name(), dataset_name, self.out_project_name)
                + item_desc.get_item_ext()
            )
            if self.sly_project_info is not None:
                dataset_info = self.get_or_create_dataset(dataset_name)
                if self.net.modality == "images":
                    if self.net.may_require_items():
                        image_info = g.api.image.upload_np(
                            dataset_info.id, out_item_name, item_desc.read_image()
                        )
                    else:
                        image_info = g.api.image.upload_id(
                            dataset_info.id, out_item_name, item_desc.info.item_info.id
                        )
                    g.api.annotation.upload_ann(image_info.id, ann)
                elif self.net.modality == "videos":
                    video_info = g.api.video.upload_path(
                        dataset_info.id, out_item_name, item_desc.item_data
                    )
                    ann_path = f"{item_desc.item_data}.json"
                    if not sly_fs.file_exists(ann_path):
                        ann_json = ann.to_json(KeyIdMap())
                        sly_json.dump_json_file(ann_json, ann_path)
                    g.api.video.annotation.upload_paths(
                        [video_info.id], [ann_path], self.output_meta
                    )
                    # sly_fs.silent_remove(item_desc.item_data)
                    # sly_fs.silent_remove(ann_path)

        yield ([item_desc, ann])
