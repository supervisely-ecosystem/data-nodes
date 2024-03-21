# coding: utf-8
from typing import Tuple

from supervisely import Annotation, Label, ProjectMeta, TagMetaCollection

from src.compute.Layer import Layer
from src.compute.classes_utils import ClassConstants
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from src.compute.dtl_utils import apply_to_labels
from src.utils import get_project_by_name, get_project_meta
from src.exceptions import BadSettingsError


class ImagesProjectLayer(Layer):
    action = "images_project"
    legacy_action = "data"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["classes_mapping", "tags_mapping"],
                "properties": {
                    "classes_mapping": {
                        "oneOf": [
                            {"type": "object", "patternProperties": {".*": {"type": "string"}}},
                            {"type": "string", "enum": ["default"]},
                        ]
                    },
                    "tags_mapping": {
                        "oneOf": [
                            {"type": "object", "patternProperties": {".*": {"type": "string"}}},
                            {"type": "string", "enum": ["default"]},
                        ]
                    },
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

        self._define_layer_project()

        if self.project_name is None:
            self.in_project_meta = ProjectMeta()
        else:
            self.in_project_meta = get_project_meta(get_project_by_name(self.project_name).id)

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

    def define_tags_mapping(self):
        if self.settings.get("tags_mapping", "default") != "default":
            self.tag_mapping = self.settings["tags_mapping"]
        else:
            Layer.define_tags_mapping(self)

    def class_mapper(self, label: Label):
        curr_class = label.obj_class.name

        if curr_class in self.cls_mapping:
            new_class = self.cls_mapping[curr_class]
        else:
            raise BadSettingsError("Can not find mapping for class", extra={"class": curr_class})

        new_tags = self.process_tags(label.tags)

        if new_class == ClassConstants.IGNORE:
            return []  # drop the figure
        elif new_class != ClassConstants.DEFAULT:
            obj_class = label.obj_class.clone(name=new_class)  # rename class
            label = label.clone(obj_class=obj_class, tags=new_tags)
        else:
            pass  # don't change
        return [label.clone(tags=new_tags)]

    def process_tags(self, tags: TagMetaCollection):
        new_tags = []
        curr_tags = tags
        for tag in curr_tags:
            if tag.name in self.tag_mapping:
                if self.tag_mapping[tag.name] == ClassConstants.IGNORE:
                    continue
                new_tags.append(tag)
        return new_tags

    def validate_source_connections(self):
        pass

    def modifies_data(self):
        return False

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el
        ann = apply_to_labels(ann, self.class_mapper)
        new_tags = self.process_tags(ann.img_tags)
        ann = ann.clone(img_tags=new_tags)
        yield (img_desc, ann)
