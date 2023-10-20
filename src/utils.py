import random
from typing import Callable, List, Optional, Tuple, Union
from collections import namedtuple
import json
import os
import shutil
from tqdm import tqdm

import supervisely as sly

import src.globals as g


LegacyProjectItem = namedtuple(
    "LegacyProjectItem",
    [
        "project_name",
        "ds_name",
        "image_name",
        "ia_data",
        "img_path",
        "ann_path",
    ],
)


def get_random_image(dataset_id: int):
    images = g.api.image.get_list(dataset_id)
    return random.choice(images)


def download_preview(project_name, dataset_name) -> Tuple[str, str]:
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
    preview_project_path = f"{g.PREVIEW_DIR}/{project_name}"
    preview_dataset_path = f"{preview_project_path}/{dataset_name}"
    ensure_dir(preview_dataset_path)
    image_id = get_random_image(dataset_info.id).id
    preview_img_path = f"{preview_dataset_path}/preview_image.jpg"
    g.api.image.download(image_id, preview_img_path)
    ann_json = g.api.annotation.download_json(image_id)
    preview_ann_path = f"{preview_dataset_path}/preview_ann.json"
    with open(preview_ann_path, "w") as f:
        json.dump(ann_json, f)

    return preview_img_path, preview_ann_path


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
    if id not in g.cache["dataset_info"]:
        try:
            dataset_info = g.api.dataset.get_info_by_id(id, raise_error=True)
        except:
            raise RuntimeError(f"Dataset {id} not found")
        g.cache["dataset_info"][id] = dataset_info
        g.cache["dataset_id"][(dataset_info.project_id, dataset_info.name)] = dataset_info.id
    return g.cache["dataset_info"][id]


def get_dataset_by_name(dataset_name: str, project_id: int) -> sly.DatasetInfo:
    key = (project_id, dataset_name)
    if key not in g.cache["dataset_id"]:
        try:
            dataset_info = g.api.dataset.get_info_by_name(project_id, dataset_name)
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
                    f"Trying to add new class ({inp_obj_class.name}) with shape ({inp_obj_class.geometry_type.geometry_name()}). Same class with different shape ({existing_obj_class.geometry_type.geometry_name()}) exists."
                )
        for inp_tag_meta in inp_meta.tag_metas:
            existing_tag_meta = full_input_meta.tag_metas.get(inp_tag_meta.name, None)
            if existing_tag_meta is None:
                full_input_meta = full_input_meta.add_tag_meta(inp_tag_meta)
            elif not existing_tag_meta.is_compatible(inp_tag_meta):
                raise RuntimeError(
                    f"Trying to add new tag ({inp_tag_meta.name}) with type ({inp_tag_meta.value_type}) and possible values ({inp_tag_meta.possible_values}). Same tag with different type ({existing_tag_meta.value_type}) or possible values ({existing_tag_meta.possible_values}) exists."
                )
    return full_input_meta


def get_all_datasets(project_id: int) -> List[sly.DatasetInfo]:
    if project_id not in g.cache["all_datasets"]:
        datasets = g.api.dataset.get_list(project_id)
        g.cache["all_datasets"][project_id] = [dataset.id for dataset in datasets]
        g.cache["dataset_info"].update(
            {
                dataset.id: dataset
                for dataset in datasets
                if dataset.id not in g.cache["dataset_info"]
            }
        )
    return [get_dataset_by_id(ds_id) for ds_id in g.cache["all_datasets"][project_id]]


def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def delete_dir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path, ignore_errors=False)


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
                shutil.rmtree(item_path)
        else:
            os.remove(item_path)
