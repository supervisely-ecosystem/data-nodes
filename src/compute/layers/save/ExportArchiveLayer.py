# coding: utf-8
import json
import os.path as osp
from typing import Tuple, Union

import cv2
import numpy as np

from supervisely.project.project import Dataset, Project, OpenMode
from supervisely.project.video_project import VideoProject, OpenMode


from supervisely import Annotation, VideoAnnotation, ProjectMeta, Bitmap, Polygon, logger, KeyIdMap
from src.compute.utils import imaging
from src.compute.utils import os_utils
from supervisely.imaging.color import random_rgb
import supervisely.io.json as sly_json
import supervisely.io.fs as sly_fs

from src.compute.dtl_utils.item_descriptor import ImageDescriptor, VideoDescriptor
from src.compute.Layer import Layer
from src.exceptions import GraphError, BadSettingsError
import src.globals as g


# save to archive
class ExportArchiveLayer(Layer):
    action = "export_archive"
    legacy_action = "save"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "properties": {
                    "images": {"type": "boolean"},  # Deprecated
                    "annotations": {"type": "boolean"},  # Deprecated
                    "visualize": {"type": "boolean"},
                },
            }
        },
    }

    @classmethod
    def draw_colored_mask(cls, ann: Annotation, color_mapping):
        h, w = ann.img_size
        line_w = int((max(w, h) + 1) / 300)
        line_w = max(line_w, 1)
        res_img = np.zeros((h, w, 3), dtype=np.uint8)

        for label in ann.labels:
            color = color_mapping.get(label.obj_class.name)
            if color is None:
                continue
            if isinstance(label.geometry, Bitmap) or isinstance(label.geometry, Polygon):
                label.geometry.draw(res_img, color)
            else:
                label.geometry.draw_contour(res_img, color, line_w)

        return res_img

    def __init__(self, config, output_folder, net):
        Layer.__init__(self, config, net=net)
        self.output_folder = output_folder

    def requires_item(self):
        return True

    def validate_dest_connections(self):
        pass

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
            raise BadSettingsError(
                "Enter name for the output archive to the input field in the 'Export Archive' layer"
            )
            # raise GraphError(
            # "Destination is not set", extra={"layer_config": self.config, "layer": self.action}
            # )

        if self.net.modality == "images":
            dst = self.dsts[0]
            self.out_project = Project(
                directory=f"{self.output_folder}/{dst}", mode=OpenMode.CREATE
            )
            with open(self.out_project.directory + "/meta.json", "w") as f:
                json.dump(self.output_meta.to_json(), f)

            # Deprecate warning
            for param in ["images", "annotations"]:
                if param in self.settings:
                    logger.warning(
                        "'save' layer: '{}' parameter is deprecated. Skipped.".format(param)
                    )

        elif self.net.modality == "videos":
            dst = self.dsts[0]
            self.out_project = VideoProject(
                directory=f"{self.output_folder}/{dst}", mode=OpenMode.CREATE
            )
            with open(self.out_project.directory + "/meta.json", "w") as f:
                json.dump(self.output_meta.to_json(), f)

    def process(
        self,
        data_el: Tuple[Union[ImageDescriptor, VideoDescriptor], Union[Annotation, VideoAnnotation]],
    ):
        item_desc, ann = data_el

        if isinstance(ann, Annotation):
            if not self.net.preview_mode:
                free_name = self.get_free_name(
                    item_desc.get_item_name(), item_desc.get_ds_name(), self.out_project.name
                )
                new_dataset_name = item_desc.get_res_ds_name()

                if self.settings.get("visualize"):
                    out_meta = self.output_meta
                    out_meta: ProjectMeta
                    cls_mapping = {}
                    for obj_class in out_meta.obj_classes:
                        color = obj_class.color
                        if color is None:
                            color = random_rgb()
                        cls_mapping[obj_class.name] = color

                    # hack to draw 'black' regions
                    cls_mapping = {
                        k: (1, 1, 1) if max(v) == 0 else v for k, v in cls_mapping.items()
                    }

                    vis_img = self.draw_colored_mask(ann, cls_mapping)
                    orig_img = item_desc.read_image()
                    comb_img = imaging.overlay_images(orig_img, vis_img, 0.5)

                    sep = np.array([[[0, 255, 0]]] * orig_img.shape[0], dtype=np.uint8)
                    img = np.hstack((orig_img, sep, comb_img))

                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    output_img_path = osp.join(
                        self.output_folder,
                        self.out_project.name,
                        new_dataset_name,
                        "visualize",
                        free_name + ".png",
                    )
                    os_utils.ensure_base_path(output_img_path)
                    cv2.imwrite(output_img_path, img)

                dataset_name = item_desc.get_res_ds_name()

                # @TODO: update dataset creation later
                out_ds_path = osp.join("results", self.out_project.name, dataset_name)
                if not self.out_project.datasets.has_key(out_ds_path):
                    self.out_project.create_dataset(dataset_name)
                out_dataset = self.out_project.datasets.get(out_ds_path)
                out_item_name = free_name + item_desc.get_item_ext()

                # net _always_ downloads images
                if item_desc.need_write():
                    out_dataset: Dataset
                    out_dataset.add_item_np(out_item_name, item_desc.item_data, ann=ann)
                else:
                    out_dataset.add_item_file(out_item_name, item_desc.get_item_path(), ann=ann)
        else:
            free_name = self.get_free_name(
                item_desc.get_item_name(), item_desc.get_ds_name(), self.out_project.name
            )
            new_dataset_name = item_desc.get_res_ds_name()

            dataset_name = item_desc.get_res_ds_name()
            if not self.out_project.datasets.has_key(dataset_name):
                self.out_project.create_dataset(dataset_name)
            out_dataset = self.out_project.datasets.get(dataset_name)
            out_item_name = free_name + item_desc.get_item_ext()

            # net _always_ downloads images
            if item_desc.need_write():
                # video
                video_ds_path = osp.join(out_dataset.directory, "video", out_item_name)
                sly_fs.copy_file(item_desc.item_data, video_ds_path)

                # ann
                ann_path = f"{osp.join(out_dataset.directory, 'ann', out_item_name)}.json"
                if not sly_fs.file_exists(ann_path):
                    ann_json = ann.to_json(KeyIdMap())
                    sly_json.dump_json_file(ann_json, ann_path)
        yield ([item_desc, ann])
