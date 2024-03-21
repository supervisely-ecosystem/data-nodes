import threading
import time
from supervisely import Application, ProjectInfo, DatasetInfo, Annotation, ProjectMeta, logger

from src.ui.ui import layout, header
from src.ui.tabs.configure import update_state, update_nodes, nodes_flow
from src.ui.tabs.presets import load_json

from src.ui.dtl.actions.input.images_project.images_project import ImagesProjectAction
from src.ui.dtl.actions.input.videos_project.videos_project import VideosProjectAction
from src.compute.dtl_utils.item_descriptor import ItemDescriptor, ImageDescriptor
from src.utils import LegacyProjectItem

import src.globals as g
import src.utils as u
from src.ui.utils import create_new_layer
from src.ui.widgets import ApplyCss
from supervisely.app.widgets import ImageAnnotationPreview

# init widget scripts
ImageAnnotationPreview()

u.clean_static_dir(g.STATIC_DIR)
app = Application(
    layout=ApplyCss("./static/css/global-styles.css", layout),
    static_dir=g.STATIC_DIR,
    session_info_extra_content=header,
    session_info_solid=True,
)


def _update_f():
    while True:
        updates = []
        while not g.update_queue.empty():
            updates.append(g.update_queue.get())
        if len(updates) == 0:
            time.sleep(0.1)
            continue
        try:
            if "load_json" in updates:
                load_json()
                continue
            if "metas" in updates:
                update_state()
            for u in updates:
                if isinstance(u, tuple):
                    if u[0] == "nodes":
                        update_nodes(u[1])
        finally:
            for _ in range(len(updates)):
                g.update_queue.task_done()
        time.sleep(0.1)


update_loop = threading.Thread(
    target=_update_f,
    name="App update loop",
    daemon=True,
)


def generate_preview_for_project(layer):
    if g.DATASET_ID:
        items = g.api.image.get_list(g.DATASET_ID)
    else:
        dss = g.api.dataset.get_list(g.PROJECT_ID)
        if len(dss) > 0:
            ds = dss[0]
            items = g.api.image.get_list(dss[0].id)
        else:
            items = []
    if len(items) > 0 and pr.type == "images":
        project_meta = ProjectMeta.from_json(g.api.project.get_meta(g.PROJECT_ID))
        item_info = items[0]
        image_path = f"{g.PREVIEW_DIR}/{layer.id}/preview_image.{item_info.ext}"
        g.api.image.download_path(item_info.id, image_path)
        ann_json = g.api.annotation.download_json(item_info.id)
        ann = Annotation.from_json(ann_json, project_meta)
        item_desc = ImageDescriptor(
            LegacyProjectItem(
                project_name=pr.name,
                ds_name=ds.name,
                item_name=".".join(item_info.name.split(".")[:-1]),
                item_info=item_info,
                ia_data={"item_ext": "." + item_info.ext},
                item_path=image_path,
                ann_path="",
            ),
            False,
        )
        logger.info("Update project preview")
        layer.set_preview_loading(True)
        layer.update_preview(item_desc, ann, project_meta)
        layer.set_preview_loading(False)


if g.PROJECT_ID:
    ds_name = "*"
    if g.DATASET_ID:
        ds: DatasetInfo = g.api.dataset.get_info_by_id(g.DATASET_ID)
        ds_name = ds.name
    pr: ProjectInfo = g.api.project.get_info_by_id(g.PROJECT_ID)
    src = [f"{pr.name}/{ds_name}"]

    if pr.type == "images":
        layer = create_new_layer(ImagesProjectAction.name)
    elif pr.type == "videos":
        layer = create_new_layer(VideosProjectAction.name)
    else:
        raise NotImplementedError(f"Project type {pr.type} is not supported")
    layer.from_json({"src": src, "settings": {"classes_mapping": "default"}})
    node = layer.create_node()
    nodes_flow.add_node(node)
    generate_preview_for_project(layer)

update_loop.start()

# if g.FILE:
#     g.updater("load_json")

app.call_before_shutdown(u.on_app_shutdown)
