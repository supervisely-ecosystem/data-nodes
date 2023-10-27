import threading
import time
from supervisely import Application

from src.ui.ui import layout, header
from src.ui.tabs.configure import update_metas, update_nodes, nodes_flow
from src.ui.tabs.presets import load_json
from src.ui.dtl.actions.data.data import DataAction
import src.globals as g
import src.utils as u
from src.ui.utils import create_new_layer

u.clean_static_dir(g.STATIC_DIR)

app = Application(layout=layout, static_dir=g.STATIC_DIR, session_info_extra_content=header)


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
                update_metas()
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
    ds = "*"
    if g.DATASET_ID:
        ds = g.api.dataset.get_info_by_id(g.DATASET_ID).name
    pr = g.api.project.get_info_by_id(g.PROJECT_ID).name
    src = [f"{pr}/{ds}"]
    layer = create_new_layer(DataAction.name)
    layer.from_json({"src": src, "settings": {"classes_mapping": "default"}})
    node = layer.create_node()
    nodes_flow.add_node(node)

if g.FILE:
    g.updater("load_json")
