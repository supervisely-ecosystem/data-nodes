# coding: utf-8

from typing import Tuple
import json
import os
import os.path as osp
import cv2
import numpy as np

from supervisely import Annotation, DatasetInfo, Project, Dataset, logger, OpenMode

from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from src.compute.Layer import Layer
from src.exceptions import GraphError, BadSettingsError

import src.globals as g


# save to archive, with GTs and checks
class ExportArchiveWithMasksLayer(Layer):
    action = "export_archive_with_masks"
    legacy_action = "save_masks"

    # out_dir, flag_name, mapping_name
    odir_flag_mapping = [
        ("masks_machine", "masks_machine", "gt_machine_color"),
        ("masks_human", "masks_human", "gt_human_color"),
    ]

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["archive_name", "masks_machine", "masks_human"],
                "properties": {
                    "archive_name": {"type": "string"},
                    "gt_machine_color": {
                        "type": "object",
                        "patternProperties": {".*": {"$ref": "#/definitions/color"}},
                    },
                    "gt_human_color": {
                        "type": "object",
                        "patternProperties": {".*": {"$ref": "#/definitions/color"}},
                    },
                    "images": {"type": "boolean"},  # Deprecated
                    "annotations": {"type": "boolean"},  # Deprecated
                    "masks_machine": {"type": "boolean"},
                    "masks_human": {"type": "boolean"},
                },
            }
        },
    }

    @classmethod
    def draw_colored_mask(cls, ann: Annotation, cls_mapping):
        h, w = ann.img_size
        res_img = np.zeros((h, w, 3), dtype=np.uint8)
        for label in ann.labels:
            color = cls_mapping.get(label.obj_class.name)
            if color is None:
                continue  # ignore now
            label.draw(res_img, color)
        return res_img

    @staticmethod
    def overlay_images(bkg_img, fg_img, fg_coeff):
        comb_img = (fg_coeff * fg_img + (1 - fg_coeff) * bkg_img).astype(np.uint8)

        black_mask = (fg_img[:, :, 0] == 0) & (fg_img[:, :, 1] == 0) & (fg_img[:, :, 2] == 0)
        comb_img[black_mask] = bkg_img[black_mask]
        comb_img = np.clip(comb_img, 0, 255)

        return comb_img

    def __init__(self, config, output_folder, net):
        Layer.__init__(self, config, net=net)

        self.output_folder = output_folder

    def requires_item(self):
        # res = self.settings['masks_human'] is True  # don't use img otherwise
        return True

    def validate_dest_connections(self):
        pass

    def validate(self):
        if self.net.preview_mode:
            return

        if len(self.dsts) == 0:
            raise ValueError(
                "Enter name for the output archive to the input field in the 'Export Archive with Masks' layer"
            )

        super().validate()
        if "gt_machine_color" in self.settings:
            for cls in self.settings["gt_machine_color"]:
                col = self.settings["gt_machine_color"][cls]
                # @TODO: is it required?
                # if np.min(col) != np.max(col):
                #     raise ValueError('"gt_machine_color"s should have equal rgb values, e.g.: [3, 3, 3].')
                if np.min(col) < 0:
                    raise BadSettingsError('Minimum "gt_machine_color" should be [0, 0, 0].')

        for _, flag_name, mapping_name in self.odir_flag_mapping:
            if self.settings[flag_name]:
                if mapping_name not in self.settings:
                    raise BadSettingsError(
                        "Color mapping {} required if {} is true.".format(mapping_name, flag_name)
                    )
                # @TODO: maybe check if all classes are present

        target_arr = ["masks_machine", "masks_human"]
        target_determ = any((self.settings[x] for x in target_arr))
        if not target_determ:
            raise BadSettingsError(
                "At least one of the options ({}) should be set to true.".format(
                    ", ".join(target_arr)
                )
            )

    def modifies_data(self):
        return False

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

    def preprocess(self):
        if self.net.preview_mode:
            return
        if self.output_meta is None:
            raise GraphError(
                "Output meta is not set. Check that node is connected", extra={"layer": self.action}
            )
        dst = self.dsts[0]
        if len(self.dsts) == 0:
            raise ValueError(
                "Enter name for the output archive to the input field in the 'Export Archive with Masks' layer"
            )
            # raise GraphError(
            # "Destination is not set", extra={"layer_config": self.config, "layer": self.action}
            # )
        self.out_project = Project(directory=f"{self.output_folder}/{dst}", mode=OpenMode.CREATE)
        with open(self.out_project.directory + "/meta.json", "w") as f:
            json.dump(self.output_meta.to_json(), f)

        # Deprecate warning
        for param in ["images", "annotations"]:
            if param in self.settings:
                logger.warning(
                    "'save_masks' layer: '{}' parameter is deprecated. Skipped.".format(param)
                )

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        item_desc, ann = data_el
        if not self.net.preview_mode:
            free_name = self.get_free_name(
                item_desc.get_item_name(), item_desc.get_ds_name(), self.out_project.name
            )

            orig_ds_info = item_desc.info.ds_info
            new_dataset_name = item_desc.get_res_ds_name()
            ds_parents = self.get_ds_parents(orig_ds_info)
            if ds_parents is None:
                nested_path = ""
            else:
                ds_parents_modified = [parent + "/datasets" for parent in ds_parents]
                nested_path = osp.join(*ds_parents_modified)

            for out_dir, flag_name, mapping_name in self.odir_flag_mapping:
                if not self.settings[flag_name]:
                    continue
                cls_mapping = self.settings[mapping_name]

                # hack to draw 'black' regions
                if flag_name == "masks_human":
                    cls_mapping = {
                        k: (1, 1, 1) if max(v) == 0 else v for k, v in cls_mapping.items()
                    }

                img = self.draw_colored_mask(ann, cls_mapping)

                if flag_name == "masks_human":
                    orig_img = item_desc.read_image()
                    comb_img = self.overlay_images(orig_img, img, 0.5)

                    sep = np.array([[[0, 255, 0]]] * orig_img.shape[0], dtype=np.uint8)
                    img = np.hstack((orig_img, sep, comb_img))

                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                output_img_path = osp.join(
                    self.out_project.directory,
                    nested_path,
                    new_dataset_name,
                    out_dir,
                    free_name + ".png",
                )

                dst_dir = osp.split(output_img_path)[0]

                def ensure_dir(dst_dir):
                    if not osp.exists(dst_dir):
                        parent, _ = osp.split(dst_dir)
                        ensure_dir(parent)
                        os.mkdir(dst_dir)

                ensure_dir(dst_dir)

                cv2.imwrite(output_img_path, img)

            out_dataset = None
            if not self.out_project.datasets.has_key(new_dataset_name):
                if ds_parents is not None:
                    nested_path = osp.join(nested_path, new_dataset_name)
                    out_dataset = self.out_project.create_dataset(new_dataset_name, nested_path)
                else:
                    out_dataset = self.out_project.create_dataset(new_dataset_name)

            if out_dataset is None:
                out_dataset = self.out_project.datasets.get(new_dataset_name)
            out_item_name = free_name + item_desc.get_item_ext()

            # net _always_ downloads images
            if item_desc.need_write() and item_desc.item_data is not None:
                out_dataset: Dataset
                out_dataset.add_item_np(out_item_name, item_desc.item_data, ann=ann)
            else:
                out_dataset.add_item_file(out_item_name, item_desc.get_item_path(), ann=ann)

        yield ([item_desc, ann])
