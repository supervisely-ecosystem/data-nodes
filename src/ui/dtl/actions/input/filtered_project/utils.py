from typing import Dict, List

import pandas as pd

from supervisely import Api, ImageInfo, ProjectInfo


SUPPORTED_ENTITY_FILTER_TYPES = [
    "images_filename",
    "images_tag",
    "objects_tag",
    "objects_class",
    "objects_annotator",
    "tagged_by_annotator",
    "issues_count",
    "job",
    "entities_collection",
]


def _format_filter_types(filter_types: List[str]):
    return ", ".join(str(filter_type) for filter_type in filter_types)


def _get_unsupported_filter_types(filters: List[Dict]):
    return [
        filter.get("type")
        for filter in filters
        if filter.get("type") not in SUPPORTED_ENTITY_FILTER_TYPES
    ]


def _get_filtered_list(api: Api, filters: List[Dict], **kwargs):
    try:
        return api.image.get_filtered_list(filters=filters, **kwargs)
    except ValueError as exc:
        unsupported_filter_types = _get_unsupported_filter_types(filters)
        if len(unsupported_filter_types) == 0:
            unsupported_filter_types = [filter.get("type") for filter in filters]
        raise ValueError(
            "Received unsupported image filter(s): "
            f"{_format_filter_types(unsupported_filter_types)}. Supported filters are: "
            f"{', '.join(SUPPORTED_ENTITY_FILTER_TYPES)}"
        ) from exc


def _get_filtered_images(api: Api, project_id: int, dataset_id: int, filters: List[Dict]):
    if any(filter.get("type") == "entities_collection" for filter in filters):
        filtered_images = _get_filtered_list(api, filters, project_id=project_id)
        if dataset_id is not None:
            filtered_images = [image for image in filtered_images if image.dataset_id == dataset_id]
        return filtered_images

    if dataset_id is not None:
        datasets = [api.dataset.get_info_by_id(dataset_id)]
    else:
        datasets = api.dataset.get_list(project_id)

    filtered_images = []
    for dataset in datasets:
        filtered_images.extend(_get_filtered_list(api, filters, dataset_id=dataset.id))
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
