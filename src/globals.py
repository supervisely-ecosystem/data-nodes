import os

from queue import Queue

from dotenv import load_dotenv

import supervisely as sly
from supervisely.app.widgets import (
    Dialog,
    Text,
    Editor,
    Container,
    Button,
    Flexbox,
    NotificationBox,
)


load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))


TEAM_ID = sly.env.team_id()
WORKSPACE_ID = sly.env.workspace_id()
USER_ID = sly.env.user_id()
DATA_DIR = "sly_task_data/data"
RESULTS_DIR = "sly_task_data/results"
PREVIEW_DIR = "sly_task_data/preview"
STATIC_DIR = "static"

sly.fs.mkdir(DATA_DIR, True)
sly.fs.mkdir(RESULTS_DIR, True)
sly.fs.mkdir(PREVIEW_DIR, True)

TEAM_FILES_PATH = "data-nodes"
PROJECT_ID = sly.env.project_id(raise_not_found=False)
DATASET_ID = sly.env.dataset_id(raise_not_found=False)
# FILE = sly.env.team_files_file(raise_not_found=False)
SUPPORTED_MODALITIES = ["images", "videos"]

SUPPORTED_MODALITIES_MAP = {
    "images": sly.ProjectType.IMAGES,
    "videos": sly.ProjectType.VIDEOS,
}


api = sly.Api()


ava_ag = api.agent.get_list_available(team_id=TEAM_ID)

MODALITY_TYPE = os.getenv("modal.state.modalityType", "images")
if PROJECT_ID is not None:
    project_type = api.project.get_info_by_id(PROJECT_ID).type
    if project_type not in SUPPORTED_MODALITIES:
        raise ValueError(
            f"Project type '{project_type}' is not supported. "
            f"Supported modalities: {', '.join(SUPPORTED_MODALITIES)}"
        )
    MODALITY_TYPE = project_type

PRESETS_PATH = os.path.join("/" + TEAM_FILES_PATH + "/presets", MODALITY_TYPE)


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


update_queue = Queue()

pipeline_running = False
pipeline_thread = None


def updater(update: str):
    global update_queue
    update_queue.put(update)


context_menu_position = None
current_dtl_json = None

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

warn_notification = NotificationBox(title="", description="", box_type="warning")
warn_notification.hide()

# Auto-connect to node
# uncomment to work:
# src/ui/ui.py line 28
# src/ui/tabs/configure.py line 158-176
# connect_node_checkbox = Checkbox("Auto-connect to node", checked=False)


@error_close_btn.click
def on_error_close():
    error_dialog.hide()


running_sessions_ids = []
