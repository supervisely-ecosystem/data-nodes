import ast
import os
from distutils.util import strtobool
from queue import Queue

import supervisely as sly
from dotenv import load_dotenv
from supervisely.app.widgets import (
    Button,
    Checkbox,
    Container,
    Dialog,
    Editor,
    Flexbox,
    NotificationBox,
    Text,
)

if sly.is_development():
    load_dotenv("local.env")
    load_dotenv(os.path.expanduser("~/supervisely.env"))

api: sly.Api = sly.Api()

TASK_ID = sly.env.task_id(raise_not_found=False)
TEAM_ID = sly.env.team_id()
WORKSPACE_ID = sly.env.workspace_id()
USER_ID = sly.env.user_id()
DATA_DIR = "sly_task_data/data"
RESULTS_DIR = "sly_task_data/results"
PREVIEW_DIR = "sly_task_data/preview"
WORKFLOW_DIR = "sly_task_data/workflow"
STATIC_DIR = "static"

if TASK_ID is not None:
    OFFLINE_SESSION_PATH = f"/offline-sessions/{TASK_ID}/workflows"
else:
    OFFLINE_SESSION_PATH = f"/TEST_WORKFLOW/task_id/workflows"
WORKFLOW_ID = 1


sly.fs.mkdir(DATA_DIR, True)
sly.fs.mkdir(RESULTS_DIR, True)
sly.fs.mkdir(PREVIEW_DIR, True)

TEAM_FILES_PATH = "data-nodes"
PROJECT_ID = sly.env.project_id(raise_not_found=False)
DATASET_ID = sly.env.dataset_id(raise_not_found=False)
FILE = sly.env.team_files_file(raise_not_found=False)
SUPPORTED_MODALITIES = ["images", "videos"]

SUPPORTED_MODALITIES_MAP = {
    "images": sly.ProjectType.IMAGES,
    "videos": sly.ProjectType.VIDEOS,
}

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

PIPELINE_TEMPLATE = os.getenv("modal.state.pipelineTemplate", None)
FILTERED_ENTITIES = []
ENTITIES_FILTERS = []
if PROJECT_ID is not None:
    ENTITIES_FILTERS = os.getenv("modal.state.entitiesFilter", [])
    if ENTITIES_FILTERS != []:
        ENTITIES_FILTERS = ast.literal_eval(ENTITIES_FILTERS)
    FILTERED_ENTITIES = os.getenv("modal.state.selectedEntities", [])
    if FILTERED_ENTITIES != []:
        FILTERED_ENTITIES = ast.literal_eval(FILTERED_ENTITIES)
    if FILTERED_ENTITIES == [] and ENTITIES_FILTERS != []:
        if DATASET_ID is not None:
            datasets = [api.dataset.get_info_by_id(DATASET_ID)]
        else:
            datasets = api.dataset.get_list(PROJECT_ID)
        FILTERED_ENTITIES = []
        for dataset in datasets:
            FILTERED_ENTITIES.extend(api.image.get_filtered_list(dataset.id, ENTITIES_FILTERS))
        if FILTERED_ENTITIES != []:
            FILTERED_ENTITIES = [entity.id for entity in FILTERED_ENTITIES]


FILTERED_DATASETS = []
selected_datasets = os.getenv("modal.state.selectedDatasets", [])
if selected_datasets != []:
    selected_datasets = ast.literal_eval(selected_datasets)
    nested_datasets = [
        api.dataset.get_nested(PROJECT_ID, dataset_id) for dataset_id in selected_datasets
    ]
    unpacked_datasets = [dataset.id for sublist in nested_datasets for dataset in sublist]
    FILTERED_DATASETS = selected_datasets + unpacked_datasets

if MODALITY_TYPE == "images":
    BATCH_SIZE = 50
else:
    BATCH_SIZE = 1

current_srcs: dict = {}

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
nodes_history = []


update_queue = Queue()
stop_updates = False

pipeline_running = False
pipeline_thread = None


def updater(update: str):
    global update_queue
    if stop_updates:
        sly.logger.debug("Skip update: %s", update)
        return
    sly.logger.debug("Put update to queue: %s", update)
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
connect_node_checkbox = Checkbox("Auto-connect node", checked=False)


@error_close_btn.click
def on_error_close():
    error_dialog.hide()


running_sessions_ids = []
disable_move = False

current = 0
total = 0
