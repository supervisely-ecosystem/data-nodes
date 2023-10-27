import os
import queue
from dotenv import load_dotenv

import supervisely as sly
from supervisely.app.widgets import Dialog, Text, Editor, Container, Button, Flexbox


load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))


TEAM_ID = sly.env.team_id()
WORKSPACE_ID = sly.env.workspace_id()
DATA_DIR = "sly_task_data/data"
RESULTS_DIR = "sly_task_data/results"
PREVIEW_DIR = "sly_task_data/preview"
STATIC_DIR = "static"
TEAM_FILES_PATH = "ml-nodes"
PROJECT_ID = sly.env.project_id(raise_not_found=False)
DATASET_ID = sly.env.dataset_id(raise_not_found=False)
FILE = sly.env.team_files_file(raise_not_found=False)
print(FILE)

api = sly.Api()

cache = {
    "workspace_info": {},
    "project_id": {},
    "project_info": {},
    "project_meta": {},
    "dataset_id": {},
    "dataset_info": {},
    "all_datasets": {},
    "last_search": "",
}

layers_count = 0
layers = {}


update_queue = queue.Queue()


def updater(update: str):
    global update_queue
    update_queue.put(update)


context_menu_position = None


error_description = Text()
error_extra_literal = Text("Extra:")
error_extra = Editor(
    "",
    height_px=300,
    language_mode="json",
    readonly=True,
    show_line_numbers=False,
    restore_default_button=False,
    highlight_active_line=False,
)
_error_icon_html = (
    "<i"
    "  v-if=\"data.slyAppDialogStatus === 'error'\""
    '  class="notification-box-icon el-icon-circle-cross information mr15"'
    '  style="font-size: 35px; color: #ff4949"'
    "></i>"
)
error_icon = Text(_error_icon_html)
error_close_btn = Button("OK", style="float: right;")
error_dialog = Dialog(
    title="Error",
    content=Container(
        widgets=[
            Flexbox(widgets=[error_icon, error_description]),
            # error_extra_literal,
            # Container(
            #     widgets=[error_extra],
            #     style="max-height: 400px; overflow-y: auto;",
            # ),
            error_close_btn,
        ],
    ),
    size="tiny",
)


@error_close_btn.click
def on_error_close():
    error_dialog.hide()
