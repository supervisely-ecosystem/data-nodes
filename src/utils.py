import random
from typing import Callable, List, Optional, Tuple, Union
from dataclasses import dataclass
import json
import os
from tqdm import tqdm
import numpy as np

import supervisely as sly
from supervisely import ProjectMeta, KeyIdMap, ImageInfo, logger, DatasetInfo
from supervisely.io.fs import remove_dir


import src.globals as g


@dataclass
class LegacyProjectItem:
    project_name: str
    ds_name: str
    ds_info: DatasetInfo
    item_name: str
    item_info: ImageInfo
    ia_data: np.ndarray
    item_path: str
    ann_path: str


def get_random_image(dataset_id: int, images_ids: List[int] = None) -> ImageInfo:
    if images_ids is None:
        images = g.api.image.get_list(dataset_id)
        if len(images) == 0:
            raise RuntimeError('No images found in the dataset (id: {}). Unable to generate preview.'.format(dataset_id))
        image = random.choice(images)
        return image
    else:
        image_id = random.choice(images_ids)
        image = g.api.image.get_info_by_id(image_id)
        return image


def get_random_video_frame(dataset_id: int):
    videos = g.api.video.get_list(dataset_id)
    video = random.choice(videos)
    frames_list = list(range(video.frames_count))
    frame_id = random.choice(frames_list)
    return video, frame_id


def download_preview_image(
    dataset_id: int, preview_img_path: str, images_ids: List[int] = None
) -> tuple:
    image = get_random_image(dataset_id, images_ids)
    g.api.image.download(image.id, preview_img_path)
    ann_json = g.api.annotation.download_json(image.id)
    return image, ann_json


def download_preview_video(
    dataset_id: int, preview_img_path: str, project_meta: ProjectMeta
) -> tuple:
    video, frame_id = get_random_video_frame(dataset_id)
    g.api.video.frame.download_path(video.id, frame_id, preview_img_path)
    ann_json = g.api.video.annotation.download(video.id)
    ann = sly.VideoAnnotation.from_json(ann_json, project_meta, KeyIdMap())
    labels = []
    frame_annotation = ann.frames.get(frame_id)
    if frame_annotation is not None:
        for figure in frame_annotation.figures:
            cur_label = sly.Label(
                figure.geometry,
                figure.parent_object.obj_class,
            )
            labels.append(cur_label)

    img_size = (video.frame_height, video.frame_width)
    ann = sly.Annotation(img_size, labels)
    ann_json = ann.to_json()
    return video, ann_json


def download_preview(
    project_name: str,
    dataset_name: str,
    project_meta: ProjectMeta,
    modality_type: str = "images",
    items_ids: List[int] = None,
) -> Tuple[str, str]:
    if modality_type not in g.SUPPORTED_MODALITIES:
        raise ValueError(f"Modality type {modality_type} is not supported")

    project_info = get_project_by_name(project_name)
    if project_info is None:
        raise RuntimeError(f"Project {project_name} not found")
    if dataset_name == "*":
        dataset_info = get_all_datasets(project_info.id)[0]
        dataset_name = dataset_info.name
    else:
        dataset_info = get_dataset_by_name(dataset_name, project_info.id)
    if dataset_info is None:
        raise RuntimeError(f"Dataset {dataset_name} not found in project {project_name}")
    elif dataset_info.items_count == 0:
        logger.error("Dataset contains no items.")  # disable preview?
    preview_project_path = f"{g.PREVIEW_DIR}/{project_name}"
    preview_dataset_path = f"{preview_project_path}/{dataset_name}"
    ensure_dir(preview_dataset_path)

    preview_img_path = f"{preview_dataset_path}/preview_image.jpg"
    preview_ann_path = f"{preview_dataset_path}/preview_ann.json"
    if modality_type == "images":
        item_info, ann_json = download_preview_image(dataset_info.id, preview_img_path, items_ids)
    elif modality_type == "videos":
        item_info, ann_json = download_preview_video(
            dataset_info.id, preview_img_path, project_meta
        )
    else:
        raise NotImplemented(f"Modality type {modality_type} is not supported")

    with open(preview_ann_path, "w") as f:
        json.dump(ann_json, f)

    return item_info, preview_img_path, preview_ann_path


def _get_project_by_name_or_id(name: str = None, id: int = None):
    if id is None:
        if name is None:
            raise ValueError("name or id must be specified")
        if name not in g.cache["project_id"]:
            try:
                project_info = g.api.project.get_info_by_name(
                    g.WORKSPACE_ID, name, raise_error=True
                )
            except:
                raise RuntimeError(f"Project {name} not found")
            g.cache["project_info"][project_info.id] = project_info
            g.cache["project_id"][name] = project_info.id
        project_id = g.cache["project_id"][name]
        return g.cache["project_info"][project_id]
    if id not in g.cache["project_info"]:
        try:
            project_info = g.api.project.get_info_by_id(
                id, expected_type=sly.ProjectType.IMAGES, raise_error=True
            )
        except:
            raise RuntimeError(f"Project {id} not found")
        g.cache["project_info"][id] = project_info
        g.cache["project_id"][project_info.name] = project_info.id
    return g.cache["project_info"][id]


def get_project_by_name(name: str) -> sly.ProjectInfo:
    return _get_project_by_name_or_id(name=name)


def get_project_by_id(id: int) -> sly.ProjectInfo:
    return _get_project_by_name_or_id(id=id)


def get_dataset_by_id(id: int = None) -> sly.DatasetInfo:
    try:
        dataset_info = g.api.dataset.get_info_by_id(id, raise_error=True)
    except:
        raise RuntimeError(f"Dataset {id} not found")
    g.cache["dataset_info"][id] = dataset_info
    g.cache["dataset_id"][(dataset_info.project_id, dataset_info.name)] = dataset_info.id
    return g.cache["dataset_info"][id]


def get_dataset_by_name(dataset_name: str, project_id: int) -> sly.DatasetInfo:
    def _get_info_by_name_tree(data, name: str):
        for ds_info, children in data.items():
            if ds_info.name == name:
                return ds_info
            if children:
                result = _get_info_by_name_tree(children, name)
                if result:
                    return result
        return None

    key = (project_id, dataset_name)
    if key not in g.cache["dataset_id"]:
        try:
            dataset_tree = g.api.dataset.get_tree(project_id)
            dataset_info = _get_info_by_name_tree(dataset_tree, dataset_name)
            if dataset_info is None:
                raise RuntimeError
        except:
            raise RuntimeError(f"Dataset {dataset_name} not found")
        g.cache["dataset_info"][dataset_info.id] = dataset_info
        g.cache["dataset_id"][key] = dataset_info.id
    dataset_id = g.cache["dataset_id"][key]
    return g.cache["dataset_info"][dataset_id]


def get_project_meta(project_id: int):
    if project_id not in g.cache["project_meta"]:
        try:
            project_meta_json = g.api.project.get_meta(project_id)
        except:
            raise RuntimeError(f"Project {project_id} not found")
        project_meta = sly.ProjectMeta.from_json(project_meta_json)
        g.cache["project_meta"][project_id] = project_meta
    return g.cache["project_meta"][project_id]


def merge_input_metas(input_metas: List[sly.ProjectMeta]) -> sly.ProjectMeta:
    full_input_meta = sly.ProjectMeta()
    for inp_meta in input_metas:
        for inp_obj_class in inp_meta.obj_classes:
            existing_obj_class = full_input_meta.obj_classes.get(inp_obj_class.name, None)
            if existing_obj_class is None:
                full_input_meta = full_input_meta.add_obj_class(inp_obj_class)
            elif existing_obj_class.geometry_type != inp_obj_class.geometry_type:
                raise RuntimeError(
                    f"When trying to add a new class '{inp_obj_class.name}' with shape type ({inp_obj_class.geometry_type.geometry_name()}), it is found that a class with the same name and a different shape type ({existing_obj_class.geometry_type.geometry_name()}) exists."
                )
        for inp_tag_meta in inp_meta.tag_metas:
            existing_tag_meta = full_input_meta.tag_metas.get(inp_tag_meta.name, None)
            if existing_tag_meta is None:
                full_input_meta = full_input_meta.add_tag_meta(inp_tag_meta)
            elif not existing_tag_meta.is_compatible(inp_tag_meta):
                raise RuntimeError(
                    f"When trying to add a new tag '{inp_tag_meta.name}' with type ({inp_tag_meta.value_type}) and possible values ({inp_tag_meta.possible_values}), it is found that a tag with the same name and a different type ({existing_tag_meta.value_type}) or possible values ({existing_tag_meta.possible_values}) exists."
                )
    return full_input_meta


def get_all_datasets(project_id: int) -> List[sly.DatasetInfo]:
    if project_id not in g.cache["all_datasets"]:
        datasets = g.api.dataset.get_list(project_id, recursive=True)
        g.cache["all_datasets"][project_id] = [dataset.id for dataset in datasets]
        g.cache["dataset_info"].update(
            {
                dataset.id: dataset
                for dataset in datasets
                if dataset.id not in g.cache["dataset_info"]
            }
        )
    dataset_infos = [get_dataset_by_id(ds_id) for ds_id in g.cache["all_datasets"][project_id]]
    return dataset_infos


def generate_src_ds_preview(saved_src, all_ds_map):
    src_preview_text = ""
    # total_img_cnt = 0
    for src in saved_src:
        src_preview_text += f"<li>{src.replace('/', ' / ')}</li>"
        # src_preview_text += f"<li>{src.replace('/', ' / ')} (items: {all_ds_map[src].images_count})</li>"
        # total_img_cnt += all_ds_map[src].items_count

    src_preview_text = f'<ul style="margin: 1px; padding: 0px 0px 0px 18px">{src_preview_text}</ul>'
    # src_preview_text += '<div class="field-description text-muted" bis_skin_checked="1">{total_img_cnt} images in selected datasets</div>'
    return src_preview_text


def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def delete_dir(dir_path):
    if os.path.exists(dir_path):
        remove_dir(dir_path)


def save_dtl_json(dtl_json):
    ensure_dir("sly_task_data")
    with open("sly_task_data/graph.json", "w") as f:
        json.dump(dtl_json, f, indent=4)


def delete_results_dir():
    delete_dir(g.RESULTS_DIR)


def create_results_dir():
    ensure_dir(g.RESULTS_DIR)


def delete_data_dir():
    delete_dir(g.DATA_DIR)


def create_data_dir():
    ensure_dir(g.DATA_DIR)


def create_workflow_dir():
    ensure_dir(g.WORKFLOW_DIR)


def delete_preview_dir():
    delete_dir(g.PREVIEW_DIR)


def create_preview_dir():
    ensure_dir(g.PREVIEW_DIR)


def create_url_html(url, name):
    return f'<a href="{url}" target="_blank">{name}</a>'


def create_urls_text(urls: List[Tuple[str, str]]):
    return f"<div>{''.join([create_url_html(*x) for x in urls])}</div>"


def get_task():
    task_id = os.environ.get("TASK_ID", None)
    if task_id is None:
        return "local"
    return task_id


def get_workspace_by_id(workspace_id) -> sly.WorkspaceInfo:
    if workspace_id not in g.cache["workspace_info"]:
        try:
            workspace_info = g.api.workspace.get_info_by_id(workspace_id)
        except:
            raise RuntimeError(f"Workspace {workspace_id} not found")
        g.cache["workspace_info"][workspace_id] = workspace_info
    return g.cache["workspace_info"][workspace_id]


def update_project_info(project_info: sly.ProjectInfo):
    updated = g.api.project.get_info_by_id(project_info.id)
    g.cache["project_info"][project_info.id] = updated
    return updated


def clean_static_dir(static_dir):
    ignore_dir = "css"
    for item in os.listdir(static_dir):
        item_path = os.path.join(static_dir, item)
        if os.path.isdir(item_path):
            if item != ignore_dir:
                remove_dir(item_path)
        else:
            os.remove(item_path)


def kill_serving_app():
    for task_id in g.running_sessions_ids:
        g.api.task.stop(task_id)
        logger.info(f"Session ID: {task_id} has been stopped")


def kill_deployed_app_by_layer_id(id: str):
    layer = g.layers[id]
    settings = layer._settings
    session_id = settings.get("session_id", None)
    if session_id is not None:
        g.api.app.stop(session_id)
    else:
        return


def clean_current_srcs():
    for layer_id in list(g.current_srcs.keys()):
        if layer_id not in g.layers.keys():
            g.current_srcs.pop(layer_id, None)


def on_app_shutdown():
    kill_serving_app()
