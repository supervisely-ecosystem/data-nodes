import threading
import time
from supervisely import Application, ProjectInfo, DatasetInfo

from src.ui.ui import layout, header
from src.ui.tabs.configure import update_state, update_nodes, nodes_flow
from src.ui.tabs.presets import load_json

from src.ui.dtl.actions.data.data import DataAction
from src.ui.dtl.actions.video_data.video_data import VideoDataAction


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

update_loop.start()

if g.PROJECT_ID:
    ds_name = "*"
    if g.DATASET_ID:
        ds: DatasetInfo = g.api.dataset.get_info_by_id(g.DATASET_ID)
        ds_name = ds.name
    pr: ProjectInfo = g.api.project.get_info_by_id(g.PROJECT_ID)
    src = [f"{pr.name}/{ds_name}"]

    if pr.type == "images":
        layer = create_new_layer(DataAction.name)
    elif pr.type == "videos":
        layer = create_new_layer(VideoDataAction.name)
    else:
        raise NotImplementedError(f"Project type {pr.type} is not supported")
    layer.from_json({"src": src, "settings": {"classes_mapping": "default"}})
    node = layer.create_node()
    nodes_flow.add_node(node)

# if g.FILE:
#     g.updater("load_json")

app.call_before_shutdown(u.on_app_shutdown)
