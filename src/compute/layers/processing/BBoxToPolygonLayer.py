# coding: utf-8

from copy import deepcopy
from typing import Tuple, Union

from supervisely import (
    Annotation,
    Polygon,
    Rectangle,
    Label,
    VideoAnnotation,
    Frame,
)
from supervisely.geometry.helpers import geometry_to_polygon

from src.compute.Layer import Layer
from src.compute.classes_utils import ClassConstants
from src.compute.dtl_utils.item_descriptor import ImageDescriptor, VideoDescriptor
from src.compute.dtl_utils import apply_to_labels, apply_to_frames
from src.exceptions import WrongGeometryError


class BBoxToPolygonLayer(Layer):
    action = "bbox_to_polygon"
    legacy_action = "bbox2poly"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["classes_mapping"],
                "properties": {
                    "classes_mapping": {
                        "type": "object",
                        "patternProperties": {".*": {"type": "string"}},
                    }
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def define_classes_mapping(self):
        for old_class, new_class in self.settings["classes_mapping"].items():
            self.cls_mapping[old_class] = {"title": new_class, "shape": Polygon.geometry_name()}
        self.cls_mapping[ClassConstants.OTHER] = ClassConstants.DEFAULT

    def modifies_data(self):
        return True

    def process(
        self,
        data_el: Tuple[Union[ImageDescriptor, VideoDescriptor], Union[Annotation, VideoAnnotation]],
    ):
        item_desc, ann = data_el

        def to_geom_rect(label: Label):
            new_title = self.settings["classes_mapping"].get(label.obj_class.name)
            if new_title is None:
                return [label]
            if not isinstance(label.geometry, Rectangle):
                raise WrongGeometryError(
                    None,
                    "Rectangle",
                    label.geometry.geometry_name(),
                    extra={"layer": self.action},
                )

            poly = geometry_to_polygon(label.geometry)[0]
            result_obj_class = label.obj_class.clone(name=new_title, geometry_type=Polygon)
            result_label = label.clone(geometry=poly, obj_class=result_obj_class)
            return [result_label]  # iterable

        def to_geom_rect_video(frame: Frame):
            new_figures = []
            for figure in frame.figures:
                new_title = self.settings["classes_mapping"].get(figure.video_object.obj_class.name)
                if new_title is None:
                    return [frame]

                if not isinstance(figure.geometry, Rectangle):
                    raise WrongGeometryError(
                        None,
                        "Rectangle",
                        figure.geometry.geometry_name(),
                        extra={"layer": self.action},
                    )

                poly = geometry_to_polygon(figure.geometry)[0]

                new_obj_class = figure.video_object.obj_class.clone(
                    name=new_title, geometry_type=Polygon
                )
                new_video_object = figure.video_object.clone(obj_class=new_obj_class)
                new_figure = figure.clone(new_video_object, poly)
                new_figures.append(new_figure)
            return [frame.clone(frame.index, new_figures)]

        if isinstance(ann, Annotation):
            ann = apply_to_labels(ann, to_geom_rect)
        else:
            ann = apply_to_frames(ann, to_geom_rect_video)
        yield item_desc, ann
