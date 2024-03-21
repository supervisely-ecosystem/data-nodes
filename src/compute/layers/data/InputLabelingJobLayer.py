# coding: utf-8
from typing import Tuple

from supervisely import Annotation, Label, ProjectMeta

from src.compute.Layer import Layer
from src.compute.classes_utils import ClassConstants
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from src.compute.dtl_utils import apply_to_labels
from src.utils import get_project_by_name, get_project_meta
from src.exceptions import BadSettingsError
import src.globals as g
from src.exceptions import GraphError


class InputLabelingJobLayer(Layer):
    action = "input_labeling_job"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["job_id", "job_dataset_id", "entities_ids", "classes", "tags"],
                "properties": {
                    "job_id": {"type": "integer"},
                    "job_dataset_id": {"type": "integer"},
                    "entities_ids": {"type": "array", "items": {"type": "integer"}},
                    "classes": {"type": "array", "items": {"type": "string"}},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

        self._define_layer_project()

        if self.project_name is None:
            self.in_project_meta = ProjectMeta()
        else:
            self.in_project_meta = get_project_meta(get_project_by_name(self.project_name).id)
            job_classes = [
                obj_class
                for obj_class in self.in_project_meta.obj_classes
                if obj_class.name in self.settings.get("classes", [])
            ]
            job_tags = [
                tag_meta
                for tag_meta in self.in_project_meta.tag_metas
                if tag_meta.name in self.settings.get("tags", [])
            ]
            self.in_project_meta = ProjectMeta(obj_classes=job_classes, tag_metas=job_tags)

    def validate(self):
        settings = self.settings
        job_id = settings.get("job_id", None)
        if job_id is None:
            raise GraphError("Labeling Job is not selected")
        super().validate()

    @classmethod
    def _split_data_src(cls, src):
        src_components = src.strip("/").split("/")
        if src_components == [""] or len(src_components) > 2:
            # Empty name or too many components.
            raise BadSettingsError(
                'Wrong "data" layer source path. Use "project_name/dataset_name" or "project_name/*"',
                extra={"layer_config": cls.config},
            )
        if len(src_components) == 1:
            # Only the project is specified, append '*' for the datasets.
            src_components.append("*")
        return src_components

    def _define_layer_project(self):
        self.project_name = None
        dataset_names = set()
        for src in self.srcs:
            project_name, dataset_name = self._split_data_src(src)
            if self.project_name is None:
                self.project_name = project_name
            elif self.project_name != project_name:
                raise BadSettingsError(
                    "Data Layer can only work with one project", extra={"layer_config": self.config}
                )
            dataset_names.add(dataset_name)
        self.dataset_names = list(dataset_names)

    def define_classes_mapping(self):
        if self.settings.get("classes_mapping", "default") != "default":
            self.cls_mapping = self.settings["classes_mapping"]
        else:
            Layer.define_classes_mapping(self)

    def class_mapper(self, label: Label):
        curr_class = label.obj_class.name

        if curr_class in self.cls_mapping:
            new_class = self.cls_mapping[curr_class]
        else:
            raise BadSettingsError("Can not find mapping for class", extra={"class": curr_class})

        if new_class == ClassConstants.IGNORE:
            return []  # drop the figure
        elif new_class != ClassConstants.DEFAULT:
            obj_class = label.obj_class.clone(name=new_class)  # rename class
            label = label.clone(obj_class=obj_class)
        else:
            pass  # don't change
        return [label]

    def validate_source_connections(self):
        pass

    def modifies_data(self):
        return False

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el
        if img_desc.info.item_info.id in self.settings["entities_ids"]:
            anns = g.api.labeling_job.get_annotations(
                self.settings["job_id"], [img_desc.info.item_info.id], self.in_project_meta
            )
            if len(anns) > 0:
                ann = anns[0]
            ann = apply_to_labels(ann, self.class_mapper)
            yield (img_desc, ann)
