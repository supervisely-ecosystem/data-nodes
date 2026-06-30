from typing import Dict, List

import pandas as pd

from supervisely import Api, ImageInfo, ProjectInfo


def _get_filtered_images(api: Api, project_id: int, dataset_id: int, filters: List[Dict]):
    if any(filter.get("type") == "entities_collection" for filter in filters):
        filtered_images = api.image.get_filtered_list(project_id=project_id, filters=filters)
        if dataset_id is not None:
            filtered_images = [image for image in filtered_images if image.dataset_id == dataset_id]
        return filtered_images

    if dataset_id is not None:
        datasets = [api.dataset.get_info_by_id(dataset_id)]
    else:
        datasets = api.dataset.get_list(project_id)

    filtered_images = []
    for dataset in datasets:
        filtered_images.extend(api.image.get_filtered_list(dataset.id, filters))
    return filtered_images


def build_filtered_table(
    api: Api, project_id: int, filtered_items_ids: List[int], dataset_id: int = None
) -> pd.DataFrame:
    if dataset_id:
        datasets = [api.dataset.get_info_by_id(dataset_id)]
    else:
        datasets = api.dataset.get_list(project_id)

    datasets_map = {ds.id: ds.name for ds in datasets}
    all_item_infos = []
    for dataset in datasets:
        item_list = api.image.get_list(dataset.id)
        # for images
        all_item_infos.extend(item_list)

    filtered_item_infos = [
        item_info for item_info in all_item_infos if item_info.id in filtered_items_ids
    ]

    columns = ["Name", "Dataset", "Shape (WxH)", "Classes", "Tags"]
    data = []
    for item_info in filtered_item_infos:
        # for images
        item_info: ImageInfo
        item_data = []
        item_data.append(item_info.name)
        item_data.append(datasets_map[item_info.dataset_id])
        item_data.append(f"{item_info.width}x{item_info.height}")
        item_data.append(item_info.labels_count)
        item_data.append(len(item_info.tags))
        data.append(item_data)

    dataframe = pd.DataFrame(data=data, columns=columns)
    return dataframe


def generate_project_description(
    api: Api,
    project_id: int,
    project_info: ProjectInfo,
    dataset_id: int = None,
    filtered_entities: list = [],
    entities_filters: list = [],
) -> str:
    filtered_project_description = (
        f"{len(filtered_entities)} {project_info.type} selected via filters"
    )
    if len(filtered_entities) == 0 and len(entities_filters) > 0:
        filtered_images = _get_filtered_images(api, project_id, dataset_id, entities_filters)

        filtered_project_description = (
            f"{len(filtered_images)} {project_info.type} selected via filters"
        )
    elif len(filtered_entities) == 0 and len(entities_filters) == 0:
        filtered_project_description = f"No filtered {project_info.type} in project"
    return filtered_project_description
