# coding: utf-8
from typing import Tuple, Union

from supervisely import (
    Annotation,
    Label,
    ProjectMeta,
    Frame,
    VideoFigure,
    VideoObject,
    VideoAnnotation,
)

from src.compute.Layer import Layer
from src.compute.classes_utils import ClassConstants
from src.compute.dtl_utils.item_descriptor import VideoDescriptor, ImageDescriptor
from src.compute.dtl_utils import apply_to_labels, apply_to_frames
from src.utils import get_project_by_name, get_project_meta
from src.exceptions import BadSettingsError


class VideosProjectLayer(Layer):
    action = "videos_project"
    legacy_action = "video_data"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["classes_mapping"],
                "properties": {
                    "classes_mapping": {
                        "oneOf": [
                            {"type": "object", "patternProperties": {".*": {"type": "string"}}},
                            {"type": "string", "enum": ["default"]},
                        ]
                    }
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

    def __str__(self) -> str:
        return self.__class__.__name__

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
                    f"{self.__str__} can only work with one project",
                    extra={"layer_config": self.config},
                )
            dataset_names.add(dataset_name)
        self.dataset_names = list(dataset_names)

    def define_classes_mapping(self):
        if self.settings.get("classes_mapping", "default") != "default":
            self.cls_mapping = self.settings["classes_mapping"]
        else:
            Layer.define_classes_mapping(self)

    def class_mapper(self, map_item: Union[Label, Frame]):
        # for preview
        if isinstance(map_item, Label):  # if self.net.preview_mode
            # map_item = label
            curr_class = map_item.obj_class.name
            if curr_class in self.cls_mapping:
                new_class = self.cls_mapping[curr_class]
            else:
                raise BadSettingsError(
                    "Can not find mapping for class", extra={"class": curr_class}
                )
            if new_class == ClassConstants.IGNORE:
                return []  # drop the figure
            elif new_class != ClassConstants.DEFAULT:
                obj_class = map_item.obj_class.clone(name=new_class)  # rename class
                map_item = map_item.clone(obj_class=obj_class)
            else:
                pass  # don't change
            return [map_item]
        else:
            # map_item = frame
            curr_frame_figures = map_item.figures
            figures = []
            for figure in curr_frame_figures:
                figure: VideoFigure
                curr_class: VideoObject = figure.video_object
                curr_class_name = curr_class._obj_class.name
                if curr_class_name in self.cls_mapping:
                    new_class = self.cls_mapping[curr_class_name]
                else:
                    raise BadSettingsError(
                        "Can not find mapping for class", extra={"class": curr_class_name}
                    )
                if new_class == ClassConstants.IGNORE:
                    return []  # drop the figure
                elif new_class != ClassConstants.DEFAULT:
                    obj_class = figure.video_object._obj_class.clone(name=new_class)  # rename class
                    video_object = VideoObject(obj_class)
                    figure = figure.clone(video_object=video_object)
                    figures.append(figure)
                else:
                    pass  # don't change
            if len(figures) > 0:
                map_item = map_item.clone(figures=[figures])
            return [map_item]

    def validate_source_connections(self):
        pass

    def modifies_data(self):
        return False

    def process(
        self,
        data_el: Tuple[Union[ImageDescriptor, VideoDescriptor], Union[Annotation, VideoAnnotation]],
    ):
        item_desc, ann = data_el

        if self.net.preview_mode:
            ann = apply_to_labels(ann, self.class_mapper)
        else:
            ann = apply_to_frames(ann, self.class_mapper)
        yield (item_desc, ann)
