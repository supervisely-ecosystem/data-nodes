# coding: utf-8
from supervisely import logger as sly_logger
from typing import Tuple
import numpy as np
from os.path import join

from src.compute.Layer import Layer
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from supervisely.nn.inference import Session
from src.compute.classes_utils import ClassConstants
from src.compute.tags_utils import TagConstants
from supervisely.collection.key_indexed_collection import KeyIndexedCollection
from supervisely import ProjectMeta, Annotation, ObjClass, TagMeta, TagCollection
import supervisely.imaging.image as sly_image
from supervisely.io.fs import silent_remove, file_exists
import src.globals as g


def postprocess(
    ann: Annotation,
    project_meta: ProjectMeta,
    model_meta: ProjectMeta,
    settings,
):
    keep_classes = settings["classes"]
    keep_tags = settings["tags"]
    res_project_meta, class_mapping, tag_meta_mapping = merge_metas(
        project_meta,
        model_meta,
        keep_classes,
        keep_tags,
        settings["model_suffix"],
        settings["use_model_suffix"],
    )

    image_tags = []
    for tag in ann.img_tags:
        if tag.meta.name not in keep_tags:
            continue
        image_tags.append(tag.clone(meta=tag_meta_mapping[tag.meta.name]))

    new_labels = []
    for label in ann.labels:
        if label.obj_class.name not in keep_classes:
            continue
        label_tags = []
        for tag in label.tags:
            if tag.meta.name not in keep_tags:
                continue
            label_tags.append(tag.clone(meta=tag_meta_mapping[tag.meta.name]))
        new_label = label.clone(
            obj_class=class_mapping[label.obj_class.name.strip()],
            tags=TagCollection(label_tags),
        )
        new_labels.append(new_label)

    res_ann = ann.clone(labels=new_labels, img_tags=TagCollection(image_tags))
    return res_ann, res_project_meta


def merge_metas(
    project_meta: ProjectMeta,
    model_meta: ProjectMeta,
    keep_model_classes,
    keep_model_tags,
    suffix,
    use_suffix: bool = False,
):
    res_meta = project_meta.clone()

    def _merge(keep_names, res_meta, project_collection, model_collection, is_class=False):
        mapping = {}  # old name to new meta
        for name in keep_names:
            model_item = model_collection.get(name)
            if model_item is None:
                continue
            res_item, res_name = find_item(project_collection, model_item, suffix, use_suffix)
            if res_item is None:
                res_item = model_item.clone(name=res_name)
                res_meta = (
                    res_meta.add_obj_class(res_item)
                    if is_class
                    else res_meta.add_tag_meta(res_item)
                )
            mapping[model_item.name.strip()] = res_item
        return res_meta, mapping

    res_meta, class_mapping = _merge(
        keep_model_classes, res_meta, res_meta.obj_classes, model_meta.obj_classes, is_class=True
    )
    res_meta, tag_mapping = _merge(
        keep_model_tags, res_meta, res_meta.tag_metas, model_meta.tag_metas, is_class=False
    )
    return res_meta, class_mapping, tag_mapping


def generate_res_name(item, suffix):
    return f"{item.name}-{suffix}"


def create_class_entry(item: ObjClass, suffix: str = None):
    title = f"{item.name}{suffix}" if suffix else item.name
    return {
        "title": title,
        "shape": item.geometry_type.geometry_name(),
        "color": item.color,
        "geometry_config": item.geometry_config,
    }


def create_tag_meta_entry(tag_meta: TagMeta, suffix: str = None):
    title = f"{tag_meta.name}{suffix}" if suffix else tag_meta.name
    return {
        "title": title,
        "value_type": tag_meta.value_type,
        "color": tag_meta.color,
    }


def find_item(
    collection: KeyIndexedCollection,
    item,
    suffix,
    use_suffix: bool = False,
):
    index = 0
    res_name = item.name.strip()
    while True:
        existing_item = collection.get(res_name.strip())
        if existing_item is None:
            if use_suffix is True:
                res_name = generate_res_name(item, suffix)
                existing_item = collection.get(res_name)
                if existing_item is not None:
                    return existing_item, None
            return None, res_name
        else:
            if existing_item == item.clone(name=res_name):
                if use_suffix is True:
                    res_name = generate_res_name(item, suffix)
                    existing_item = collection.get(res_name)
                    if existing_item is None:
                        return None, res_name
                    elif existing_item == item.clone(name=res_name):
                        res_name = generate_res_name(item, suffix)
                        existing_item = collection.get(res_name)
                        if existing_item is None:
                            return None, res_name
                        return existing_item, None
                    else:
                        index += 1
                        res_name = generate_res_name(item, suffix)
                        existing_item = collection.get(res_name)
                        if existing_item is None:
                            return None, res_name
                return existing_item, None
            else:
                res_name = generate_res_name(item, suffix)
                index += 1


class ApplyNN(Layer):
    action = "apply_nn"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": [
                    "current_meta",
                    "session_id",
                    "model_info",
                    "model_meta",
                    "model_settings",
                    "model_suffix",
                    "use_model_suffix",
                    "add_pred_ann_method",
                    "apply_method",
                    "classes",
                    "tags",
                ],
                "properties": {
                    "current_meta": {"type": "object"},
                    "session_id": {"oneOf": [{"type": "integer"}, {"type": "null"}]},
                    "model_info": {"type": "object"},
                    "model_meta": {"type": "object"},
                    "model_settings": {"type": "object"},
                    "model_suffix": {"type": "string"},
                    "use_model_suffix": {"type": "boolean"},
                    "add_pred_ann_method": {"type": "string", "enum": ["merge", "replace"]},
                    "apply_method": {"type": "string", "enum": ["image", "roi", "sliding_window"]},
                    "classes": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}},
                        ]
                    },
                    "tags": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "array", "items": {"type": "string"}},
                        ]
                    },
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def requires_item(self):
        return True

    def modifies_data(self):
        return True

    def define_classes_mapping(self):
        current_meta = ProjectMeta().from_json(self.settings["current_meta"])
        model_meta = ProjectMeta().from_json(self.settings["model_meta"])
        classes = self.settings["classes"]
        suffix = self.settings["model_suffix"]
        use_suffix = self.settings["use_model_suffix"]
        add_pred_ann_method = self.settings["add_pred_ann_method"]

        new_classes = []
        add_pred_ann_method = self.settings["add_pred_ann_method"]
        if use_suffix is True:
            for model_class in model_meta.obj_classes:
                if model_class.name in classes:
                    new_classes.append(create_class_entry(model_class, f"-{suffix}"))

        elif add_pred_ann_method == "replace":
            for model_class in model_meta.obj_classes:
                if model_class.name in classes:
                    curr_class = current_meta.get_obj_class(model_class.name)
                    if curr_class is None:
                        new_classes.append(create_class_entry(model_class))
                    else:
                        self.cls_mapping[model_class.name] = create_class_entry(model_class)

        elif add_pred_ann_method == "merge":
            for model_class in model_meta.obj_classes:
                if model_class.name in classes:
                    curr_class = current_meta.get_obj_class(model_class.name)
                    if curr_class is not None:
                        new_classes.append(create_class_entry(model_class, f"-{suffix}"))
                    else:
                        new_classes.append(create_class_entry(model_class))

        self.cls_mapping[ClassConstants.OTHER] = ClassConstants.DEFAULT
        self.cls_mapping[ClassConstants.NEW] = new_classes

    def define_tags_mapping(self):
        current_meta = ProjectMeta().from_json(self.settings["current_meta"])
        model_meta = ProjectMeta().from_json(self.settings["model_meta"])
        tags = self.settings["tags"]
        use_suffix = self.settings["use_model_suffix"]
        suffix = self.settings["model_suffix"]

        new_tag_metas = []
        for model_tag_meta in model_meta.tag_metas:
            if model_tag_meta.name in tags:
                curr_tag_meta = current_meta.get_tag_meta(model_tag_meta.name)
                if use_suffix:
                    new_tag_metas.append(create_tag_meta_entry(model_tag_meta, f"-{suffix}"))
                elif curr_tag_meta is not None:
                    new_tag_metas.append(create_tag_meta_entry(model_tag_meta, f"-{suffix}"))
                else:
                    new_tag_metas.append(create_tag_meta_entry(model_tag_meta))

        self.tag_mapping[TagConstants.OTHER] = TagConstants.DEFAULT
        self.tag_mapping[TagConstants.NEW] = new_tag_metas

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el
        img = img_desc.read_image()
        img = img.astype(np.uint8)

        if self.settings["session_id"] is None:
            raise ValueError("Apply NN layer requires model to be connected")
        else:
            img_path = join(
                f"{g.PREVIEW_DIR}",
                f"{img_desc.info.item_name}{img_desc.info.ia_data['item_ext']}",
            )

            model_meta = ProjectMeta().from_json(self.settings["model_meta"])
            apply_method = self.settings["apply_method"]
            if apply_method == "image":
                sly_image.write(img_path, img)
                session = Session(g.api, self.settings["session_id"])
                try:
                    pred_ann = session.inference_image_path(img_path)
                    pred_ann, res_meta = postprocess(
                        pred_ann, self.output_meta, model_meta, self.settings
                    )
                except:
                    sly_logger.debug("Could not apply model to image")
                    pred_ann = Annotation(img_size=img.shape[:2])

                if file_exists(img_path):
                    silent_remove(img_path)

            elif apply_method == "roi":
                pass
            elif apply_method == "sliding_window":
                pass

            add_pred_ann_method = self.settings["add_pred_ann_method"]
            if add_pred_ann_method == "merge":
                ann = ann.merge(pred_ann)
            elif add_pred_ann_method == "replace":
                ann = pred_ann

            new_img_desc = img_desc.clone_with_item(img)
            yield new_img_desc, ann

    def validate(self):
        super().validate()
        if self.settings["session_id"] is None:
            raise ValueError("Apply NN layer requires model to be connected")
