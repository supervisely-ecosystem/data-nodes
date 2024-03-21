from typing import List, Union
from supervisely import (
    ProjectMeta,
    TagMeta,
    TagMetaCollection,
    ObjClass,
    ObjClassCollection,
    ProjectInfo,
    DatasetInfo,
)
from supervisely.app.widgets import Select, Text, DatasetThumbnail, Button
from supervisely.api.labeling_job_api import LabelingJobInfo

import src.globals as g
import src.utils as utils
from src.ui.widgets import ClassesListPreview, TagsListPreview, LabelingJobInfoWidget


def get_job_meta(job_info: LabelingJobInfo):
    project_meta = utils.get_project_meta(job_info.project_id)
    job_classes = [
        obj_class
        for obj_class in project_meta.obj_classes
        if obj_class.name in job_info.classes_to_label
    ]
    job_tags = [
        tag_meta for tag_meta in project_meta.tag_metas if tag_meta.name in job_info.tags_to_label
    ]
    job_meta = ProjectMeta(obj_classes=job_classes, tag_metas=job_tags)
    return job_meta


# PREVIEW
def set_job_name_preview(job_name: str, lj_selector_preview_lj_text: Text):
    lj_selector_preview_lj_text.set(f"Job name: {job_name}", "text")


def set_job_status_preview(job_status: str, lj_selector_preview_lj_status: Text):
    if job_status == "pending":
        job_status = "Pending"
    elif job_status == "in_progress":
        job_status = "In progress"
    elif job_status == "on_review":
        job_status = "On review"
    elif job_status == "completed":
        job_status = "Completed"
    elif job_status == "stopped":
        job_status = "Stopped"

    lj_selector_preview_lj_status.set(f"Job status: {job_status}", "text")
    lj_selector_preview_lj_status.show()


def set_job_progress_preview(job_info: LabelingJobInfo, lj_selector_preview_lj_progress: Text):
    job_status = job_info.status
    if job_status == "in_progress":
        lj_selector_preview_lj_progress.set(
            f"Job progress: {job_info.finished_images_count} / {job_info.images_count}", "text"
        )
    else:  # job_status == "on_review" or job_status == "completed" or job_status == "stopped":
        lj_selector_preview_lj_progress.set(
            f"Job progress: {job_info.accepted_images_count} / {job_info.images_count}", "text"
        )
    lj_selector_preview_lj_progress.show()


def set_job_dataset_preview(
    project_info: ProjectInfo,
    dataset_info: DatasetInfo,
    lj_selector_preview_lj_dataset_thumbnail: DatasetThumbnail,
):
    lj_selector_preview_lj_dataset_thumbnail.set(project_info, dataset_info)
    lj_selector_preview_lj_dataset_thumbnail.show()


def set_job_classes_preview(
    job_classes: Union[List[ObjClass], ObjClassCollection],
    lj_selector_preview_classes: ClassesListPreview,
    lj_selector_preview_classes_text: Text,
    show_counter: bool = True,
):
    lj_selector_preview_classes.set(job_classes)
    if show_counter:
        lj_selector_preview_classes_text.set(
            f"Classes: {len(job_classes)} / {len(job_classes)}", "text"
        )
    else:
        lj_selector_preview_classes_text.set("Classes", "text")


def set_job_tags_preview(
    job_tags: Union[List[TagMeta], TagMetaCollection],
    lj_selector_preview_tags: TagsListPreview,
    lj_selector_preview_tags_text: Text,
    show_counter: bool = True,
):
    lj_selector_preview_tags.set(job_tags)
    if show_counter:
        lj_selector_preview_tags_text.set(f"Tags: {len(job_tags)} / {len(job_tags)}", "text")
    else:
        lj_selector_preview_tags_text.set(f"Tags", "text")


# --------------------------


# SETTINGS FROM JSON
def set_job_thumbnail_from_json(
    job_info: LabelingJobInfo,
    lj_selector_preview_lj_dataset_thumbnail: DatasetThumbnail,
    lj_selector_preview_lj_text: Text,
):
    project_info = g.api.project.get_info_by_id(job_info.project_id)
    if project_info is None:
        lj_selector_preview_lj_text.set(
            f"Project: {job_info.project_name} (ID {job_info.project_id}) not found",
            "warning",
        )
        return False

    dataset_info = g.api.dataset.get_info_by_id(job_info.dataset_id)
    set_job_dataset_preview(project_info, dataset_info, lj_selector_preview_lj_dataset_thumbnail)
    return True


def set_job_from_json(
    settings: dict,
    lj_selector_sidebar_selector: Select,
    lj_selector_sidebar_lj_info: LabelingJobInfoWidget,
):
    job_id = settings.get("job_id", None)
    lj_selector_sidebar_selector.set_value(job_id)
    lj_selector_sidebar_lj_info.set_id(job_id)


def set_settings_from_json(
    settings: dict,
    lj_selector_preview_lj_dataset_thumbnail: DatasetThumbnail,
    lj_selector_sidebar_selector: Select,
    lj_selector_sidebar_lj_info: LabelingJobInfoWidget,
    lj_selector_preview_lj_text: Text,
    lj_selector_preview_classes: ClassesListPreview,
    lj_selector_preview_tags: TagsListPreview,
    update_preview_btn: Button,
):
    job_id = settings.get("job_id", None)
    if job_id is None:
        return

    job_info = g.api.labeling_job.get_info_by_id(job_id)

    project_exists = set_job_thumbnail_from_json(
        job_info, lj_selector_preview_lj_dataset_thumbnail, lj_selector_preview_lj_text
    )
    if not project_exists:
        return

    set_job_from_json(settings, lj_selector_sidebar_selector, lj_selector_sidebar_lj_info)
    set_job_name_preview(job_info.name, lj_selector_preview_lj_text)

    job_meta = get_job_meta(job_info)
    classes = settings.get("classes", [])
    job_classes = [obj_class for obj_class in job_meta.obj_classes if obj_class.name in classes]
    set_job_classes_preview(job_classes, lj_selector_preview_classes)

    tags = settings.get("tags", [])
    job_tags = [tag_meta for tag_meta in job_meta.tag_metas if tag_meta.name in tags]
    set_job_tags_preview(job_tags, lj_selector_preview_tags)
    update_preview_btn.enable()


# --------------------------


def save_settings(job_info: LabelingJobInfo) -> dict:
    if job_info is None:
        return {
            "job_id": None,
            "job_dataset_id": None,
            "entities_ids": [],
            "classes": [],
            "tags": [],
        }
    return {
        "job_id": job_info.id,
        "job_dataset_id": job_info.dataset_id,
        "entities_ids": [entity["id"] for entity in job_info.entities],
        "classes": job_info.classes_to_label,
        "tags": job_info.tags_to_label,
    }
