# coding: utf-8

from typing import Tuple

import supervisely as sly

from src.compute.dtl_utils.image_descriptor import ImageDescriptor
from src.compute.Layer import Layer
from src.exceptions import GraphError
import src.globals as g


def _get_source_projects_ids_from_dtl():
    source_projects_ids = []
    for action in g.current_dtl_json:
        if action["action"] == "data":
            if len(action["src"]) == 0:
                continue
            project_name = action["src"][0].split("/")[0]
            project_id = g.api.project.get_info_by_name(g.WORKSPACE_ID, project_name).id
            source_projects_ids.append(project_id)
    return source_projects_ids


class SuperviselyLayer(Layer):
    action = "supervisely"

    layer_settings = {"required": ["settings"], "properties": {"settings": {}}}

    def __init__(self, config, output_folder, net):
        Layer.__init__(self, config, net=net)
        self.output_folder = output_folder
        self.sly_project_info = None

    def is_archive(self):
        return False

    def validate_dest_connections(self):
        for dst in self.dsts:
            if len(dst) == 0:
                raise ValueError("Destination name in '{}' layer is empty!".format(self.action))

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
        self.out_project_name = dst

        self.sly_project_info = g.api.project.create(
            g.WORKSPACE_ID,
            self.out_project_name,
            type=sly.ProjectType.IMAGES,
            change_name_if_conflict=True,
        )
        g.api.project.update_meta(self.sly_project_info.id, self.output_meta)

        custom_data = {
            "source_projects": _get_source_projects_ids_from_dtl(),
            "ml-nodes": g.current_dtl_json,
        }
        g.api.project.update_custom_data(self.sly_project_info.id, custom_data)
        self.need_image = self.net.may_require_images()

    def get_or_create_dataset(self, dataset_name):
        if not g.api.dataset.exists(self.sly_project_info.id, dataset_name):
            return g.api.dataset.create(self.sly_project_info.id, dataset_name)
        else:
            return g.api.dataset.get_info_by_name(self.sly_project_info.id, dataset_name)

    def process(self, data_el: Tuple[ImageDescriptor, sly.Annotation]):
        img_desc, ann = data_el

        if not self.net.preview_mode:
            dataset_name = img_desc.get_res_ds_name()
            out_item_name = (
                self.net.get_free_name(img_desc, self.out_project_name) + img_desc.get_image_ext()
            )

            if self.sly_project_info is not None:
                dataset_info = self.get_or_create_dataset(dataset_name)
                if self.need_image:
                    image_info = g.api.image.upload_np(
                        dataset_info.id, out_item_name, img_desc.read_image()
                    )
                else:
                    image_info = g.api.image.copy(
                        dataset_info.id, img_desc.info.image_info.id, change_name_if_conflict=True
                    )

                g.api.annotation.upload_ann(image_info.id, ann)

        yield ([img_desc, ann],)
