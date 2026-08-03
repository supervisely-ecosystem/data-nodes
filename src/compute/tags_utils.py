# coding: utf-8

from typing import List, Optional, Tuple

import supervisely as sly
from supervisely import Annotation, Label, Tag, TagCollection

import src.globals as g


ALLOW_DUPLICATE_TAGS_SETTING = "allowDuplicateTags"


class TagConstants:
    OTHER = "__other__"
    IGNORE = "__ignore__"
    DEFAULT = "__default__"
    UPDATE = "__update__"
    NEW = "__new__"
    CLONE = "__clone__"


def is_duplicate_tags_allowed(project_id: int) -> bool:
    """Read the 'Multiple tags mode' setting of the project.

    :param project_id: Destination project ID.
    :return: True if the same tag can be assigned to an image or an object more than once.
    """
    project_settings = g.api.project.get_settings(project_id)
    if ALLOW_DUPLICATE_TAGS_SETTING not in project_settings:
        sly.logger.debug(
            f"Project ID: '{project_id}' has no '{ALLOW_DUPLICATE_TAGS_SETTING}' setting. "
            "Duplicate tags are considered to be not allowed"
        )
        return False
    return project_settings[ALLOW_DUPLICATE_TAGS_SETTING]


def remove_duplicate_tags(
    anns: List[Annotation], image_ids: List[int], allow_duplicate_tags: bool
) -> List[Annotation]:
    """Remove tags that the destination project will not accept: if 'Multiple tags mode' is
    disabled, only the first tag with each name is kept on an image and on every object.

    :param anns: Annotations to upload.
    :param image_ids: Destination image IDs, used in warnings.
    :param allow_duplicate_tags: 'Multiple tags mode' setting of the destination project.
    :return: Annotations without duplicate tags.
    """
    if allow_duplicate_tags:
        return anns

    result_anns: List[Annotation] = []
    for ann, image_id in zip(anns, image_ids):
        result_ann = _remove_duplicate_tags_from_ann(ann, image_id)
        result_anns.append(result_ann)
    return result_anns


def _remove_duplicate_tags_from_ann(ann: Annotation, image_id: int) -> Annotation:
    """Keep only the first tag with each name on the image and on every object.

    :param ann: Annotation to clean up.
    :param image_id: Destination image ID, used in warnings.
    :return: Annotation without duplicate tags.
    """
    image_tags, removed_image_tags = _keep_first_tag_of_each_name(ann.img_tags)
    for tag in removed_image_tags:
        _log_removed_tag(tag, image_id, object_name=None)

    removed_object_tags_count = 0
    result_labels: List[Label] = []
    for label in ann.labels:
        object_tags, removed_object_tags = _keep_first_tag_of_each_name(label.tags)
        for tag in removed_object_tags:
            _log_removed_tag(tag, image_id, object_name=label.obj_class.name)
        removed_object_tags_count += len(removed_object_tags)
        result_label = label.clone(tags=object_tags)
        result_labels.append(result_label)

    if len(removed_image_tags) == 0 and removed_object_tags_count == 0:
        return ann
    return ann.clone(labels=result_labels, img_tags=image_tags)


def _keep_first_tag_of_each_name(tags: TagCollection) -> Tuple[TagCollection, List[Tag]]:
    """Split tags into the first tag of each name and the rest of them.

    :param tags: Tags of an image or of an object.
    :return: Kept tags and removed duplicates.
    """
    kept_tags: List[Tag] = []
    kept_tag_names: List[str] = []
    removed_tags: List[Tag] = []
    for tag in tags:
        if tag.name in kept_tag_names:
            removed_tags.append(tag)
            continue
        kept_tag_names.append(tag.name)
        kept_tags.append(tag)
    return TagCollection(kept_tags), removed_tags


def _log_removed_tag(tag: Tag, image_id: int, object_name: Optional[str]) -> None:
    """Warn that a duplicate tag is not uploaded.

    :param tag: Removed tag.
    :param image_id: Destination image ID.
    :param object_name: Class name of the object the tag belongs to, None for an image tag.
    """
    if object_name is None:
        target = f"Image (ID: '{image_id}')"
    else:
        target = f"Object '{object_name}' on image (ID: '{image_id}')"
    sly.logger.warn(
        f"{target} already has tag '{tag.name}'. "
        f"Duplicate with value '{tag.value}' is skipped: "
        "'Multiple tags mode' is disabled in the destination project settings"
    )
