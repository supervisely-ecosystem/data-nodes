# coding: utf-8

from typing import Dict, List, Optional

import supervisely as sly
from supervisely import ProjectMeta

from src.compute.tags_utils import ALLOW_DUPLICATE_TAGS_SETTING
import src.globals as g


LABELING_INTERFACE_SETTING = "labelingInterface"
GROUP_IMAGES_SETTING = "groupImages"
GROUP_IMAGES_BY_TAG_ID_SETTING = "groupImagesByTagId"
GROUP_IMAGES_SYNC_SETTING = "groupImagesSync"


def copy_project_settings(source_project_ids: List[int], destination_project_id: int) -> None:
    """Copy settings of the source project to the project created by the pipeline.
    Must be called after the meta of the created project is updated.

    :param source_project_ids: Source project IDs of the pipeline, the first one is used.
    :param destination_project_id: ID of the created project.
    """
    if len(source_project_ids) == 0:
        sly.logger.warn("Source project is not found in the pipeline, settings are not copied")
        return

    source_project_id = source_project_ids[0]
    if len(source_project_ids) > 1:
        sly.logger.info(
            f"Pipeline has {len(source_project_ids)} source projects. "
            f"Settings of the project ID: '{source_project_id}' are copied to the created project"
        )

    source_settings = g.api.project.get_settings(source_project_id)
    settings_to_copy: Dict = {}
    for setting_name in [ALLOW_DUPLICATE_TAGS_SETTING, LABELING_INTERFACE_SETTING]:
        if setting_name in source_settings:
            settings_to_copy[setting_name] = source_settings[setting_name]

    group_images_settings = _match_group_images_settings(
        source_settings, source_project_id, destination_project_id
    )
    settings_to_copy.update(group_images_settings)

    if len(settings_to_copy) == 0:
        return

    g.api.project.update_settings(destination_project_id, settings_to_copy, merge_with_current=True)
    sly.logger.info(
        f"Settings of the project ID: '{source_project_id}' are copied "
        f"to the created project ID: '{destination_project_id}': {settings_to_copy}"
    )


def _match_group_images_settings(
    source_settings: Dict, source_project_id: int, destination_project_id: int
) -> Dict:
    """Repeat multi-view settings of the source project, the group tag is matched by name.

    :param source_settings: Settings of the source project.
    :param source_project_id: Source project ID.
    :param destination_project_id: ID of the created project.
    :return: Multi-view settings, empty if multi-view mode is disabled in the source project.
    """
    if GROUP_IMAGES_SETTING not in source_settings:
        return {}
    if source_settings[GROUP_IMAGES_SETTING] is not True:
        return {}
    if GROUP_IMAGES_BY_TAG_ID_SETTING not in source_settings:
        return {}

    source_group_tag_id = source_settings[GROUP_IMAGES_BY_TAG_ID_SETTING]
    group_tag_id = _match_group_tag_id(
        source_group_tag_id, source_project_id, destination_project_id
    )
    if group_tag_id is None:
        sly.logger.warn(
            f"Group tag of the project ID: '{source_project_id}' is not found "
            "in the created project. Multi-view mode is not enabled"
        )
        return {}

    group_images_sync = False
    if GROUP_IMAGES_SYNC_SETTING in source_settings:
        group_images_sync = source_settings[GROUP_IMAGES_SYNC_SETTING]
    return {
        GROUP_IMAGES_SETTING: True,
        GROUP_IMAGES_BY_TAG_ID_SETTING: group_tag_id,
        GROUP_IMAGES_SYNC_SETTING: group_images_sync,
    }


def _match_group_tag_id(
    source_group_tag_id: Optional[int], source_project_id: int, destination_project_id: int
) -> Optional[int]:
    """Find the group tag of the source project in the created project by name.

    :param source_group_tag_id: Group tag ID in the source project.
    :param source_project_id: Source project ID.
    :param destination_project_id: ID of the created project.
    :return: Group tag ID in the created project, None if the tag is not found.
    """
    if source_group_tag_id is None:
        return None

    source_meta_json = g.api.project.get_meta(source_project_id)
    source_meta = ProjectMeta.from_json(source_meta_json)
    group_tag_name = source_meta.get_tag_name_by_id(source_group_tag_id)
    if group_tag_name is None:
        return None

    destination_meta_json = g.api.project.get_meta(destination_project_id)
    destination_meta = ProjectMeta.from_json(destination_meta_json)
    group_tag_meta = destination_meta.get_tag_meta(group_tag_name)
    if group_tag_meta is None:
        return None
    return group_tag_meta.sly_id
