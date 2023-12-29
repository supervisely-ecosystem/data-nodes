# coding: utf-8
from typing import Tuple, List

from supervisely import (
    Annotation,
    Label,
    ProjectMeta,
    Bitmap,
    PointLocation,
    Tag,
    Point,
    Polygon,
    Rectangle,
    Polyline,
)

from src.compute.Layer import Layer
from src.compute.classes_utils import ClassConstants
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from src.compute.dtl_utils import apply_to_labels
from src.utils import get_project_by_name, get_project_meta
from src.exceptions import BadSettingsError
import src.globals as g


def get_geometry(type: str, data: dict):
    if type == "bitmap":
        mask = Bitmap.base64_2_data(data["bitmap"]["data"])
        origin = data["bitmap"]["origin"]
        origin = PointLocation(origin[1], origin[0])
        geometry = Bitmap(mask, origin)

    elif type == "point":  # points
        row, col = data["points"]["exterior"][0][1], data["points"]["exterior"][0][0]
        geometry = Point(row, col)

    elif type == "rectangle":  # points
        top, left, bottom, right = (
            data["points"]["exterior"][0][1],
            data["points"]["exterior"][0][0],
            data["points"]["exterior"][1][1],
            data["points"]["exterior"][1][0],
        )
        geometry = Rectangle(top, left, bottom, right)

    elif type == "polygon":  # points
        exterior = [PointLocation(coord[1], coord[0]) for coord in data["points"]["exterior"]]
        interior = [PointLocation(coord[1], coord[0]) for coord in data["points"]["interior"]]
        geometry = Polygon(exterior, interior)

    elif type == "line":  # points
        exterior = [PointLocation(coord[1], coord[0]) for coord in data["points"]["exterior"]]
        geometry = Polyline(exterior)

    else:
        geometry = None

    return geometry


def create_tags_from_labeling_job(job_tags_map: List[dict], project_meta: ProjectMeta) -> List[Tag]:
    tags = []
    for tag in job_tags_map:
        tag_meta = project_meta.get_tag_meta_by_id(tag["tagId"])
        if tag_meta is None:
            continue
        tag_value = tag.get("value", None)
        tag = Tag(tag_meta, value=tag_value)
        tags.append(tag)
    return tags


def create_labels_from_labeling_job(
    figures_map: List[dict], project_meta: ProjectMeta
) -> List[Label]:
    labels = []
    for figure in figures_map:
        obj_class = project_meta.get_obj_class_by_id(figure["classId"])
        if obj_class is None:
            continue
        geometry = get_geometry(figure["geometryType"], figure["geometry"])
        if geometry is None:
            continue
        tags = create_tags_from_labeling_job(figure["tags"], project_meta)

        label = Label(obj_class=obj_class, geometry=geometry, tags=tags)
        labels.append(label)
    return labels


def create_ann_from_labeling_job(
    settings: dict,
    image_id: Tuple[int, int],
    project_meta: ProjectMeta,
) -> Annotation:
    g.api.add_header("x-job-id", str(settings["job_id"]))
    figures = [
        figure
        for figure in g.api.figure.get_list(settings["job_dataset_id"])["entities"]
        if image_id == figure["entityId"]
    ]
    image = g.api.image.get_info_by_id(image_id)
    g.api.pop_header("x-job-id")

    img_tags = create_tags_from_labeling_job(image.tags, project_meta)
    labels = create_labels_from_labeling_job(figures, project_meta)
    ann = Annotation(img_size=(image.height, image.width), labels=labels, img_tags=img_tags)
    return ann


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
                if obj_class.name in self.settings["classes"]
            ]
            job_tags = [
                tag_meta
                for tag_meta in self.in_project_meta.tag_metas
                if tag_meta.name in self.settings["tags"]
            ]
            self.in_project_meta = ProjectMeta(obj_classes=job_classes, tag_metas=job_tags)

    def validate(self):
        settings = self.settings
        job_id = settings.get("job_id", None)
        if job_id is None:
            raise RuntimeError("Labeling Job is not selected")
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
            # take ann from lj
            ann = create_ann_from_labeling_job(
                self.settings, img_desc.info.item_info.id, self.in_project_meta
            )
            ann = apply_to_labels(ann, self.class_mapper)
            yield (img_desc, ann)
