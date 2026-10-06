import os
import threading
from pathlib import Path

import src.globals as g
import src.ui.utils as ui_utils
import src.utils as utils
import src.workflow as w
import supervisely as sly
from src.compute.layers.data.FilteredProjectLayer import FilteredProjectLayer
from src.compute.layers.data.ImagesProjectLayer import ImagesProjectLayer
from src.compute.layers.data.InputLabelingJobLayer import InputLabelingJobLayer
from src.compute.layers.data.VideosProjectLayer import VideosProjectLayer
from src.compute.layers.save.AddToExistingProjectLayer import AddToExistingProjectLayer
from src.compute.layers.save.CopyAnnotationsLayer import CopyAnnotationsLayer
from src.compute.layers.save.CreateLabelingJobLayer import CreateLabelingJobLayer
from src.compute.layers.save.CreateNewProjectLayer import CreateNewProjectLayer
from src.compute.layers.save.OutputProjectLayer import OutputProjectLayer
from src.compute.main import main as compute_dtls
from src.compute.utils.stat_timer import global_timer
from src.exceptions import CustomException, handle_exception
from src.ui.tabs.configure import nodes_flow, nodes_flow_card
from src.ui.widgets import CircleProgress
from supervisely.app.widgets import (
    Button,
    Container,
    Dialog,
    Empty,
    NotificationBox,
    Progress,
    ReloadableArea,
    Text,
)
from supervisely.io.fs import get_file_size

show_run_dialog_btn = Button(
    "Run",
    icon="zmdi zmdi-play",
    button_size="small",
    style="border: 1px solid rgb(191, 203, 217); margin: 10px 0px 0px 25px; padding: 9px 13px; border-radius: 6px; font-size: 12px; text-transform: uppercase; font-weight: 500; background-color: #448dff; color: white; border-color: transparent; height: 32px;",
)
show_run_dialog_btn_running = Button(
    "Running",
    icon="el-icon-loading",
    button_size="small",
    style="border: 1px solid rgb(191, 203, 217); margin: 10px 0px 0px 25px; padding: 9px 13px; border-radius: 6px; font-size: 12px; text-transform: uppercase; font-weight: 500; background-color: #448dff; color: white; border-color: transparent; height: 32px;",
)
show_run_dialog_btn_running.hide()
run_btn = Button("Run", icon="zmdi zmdi-play")
stop_btn = Button("Stop", icon="zmdi zmdi-stop", button_type="danger")
stop_btn.hide()

progress = Progress(hide_on_finish=False)
circle_progress = CircleProgress(progress)
circle_progress.hide()
download_archives_urls = Text("")
results = ReloadableArea(Empty())
results.hide()

error_notification = NotificationBox(title="Error", description="", box_type="error")
error_notification.hide()

layout = Container(
    widgets=[
        run_btn,
        stop_btn,
        progress,
        error_notification,
        g.warn_notification,
        download_archives_urls,
        results,
    ]
)


def _run():
    run_btn.hide()
    stop_btn.show()

    nodes_flow_card.lock()

    circle_progress.set_status("none")
    circle_progress.show()

    error_notification.hide()

    if not g.pipeline_running:
        return

    g.disable_move = False
    edges = nodes_flow.get_edges_json()
    nodes_state = nodes_flow.get_nodes_state_json()

    run_btn.hide()
    results.hide()
    progress(message="Validating...", total=1, position=0)
    progress.show()

    try:
        for node_id in nodes_state:
            node = g.layers.get(node_id)
            if node is not None:
                node.before_run()

        # init layers
        ui_utils.init_layers(nodes_state)

        # init layers sources
        # destinations are defined in init_layers
        ui_utils.init_src(edges)

        if not g.pipeline_running:
            return

        # prepare results dir
        utils.delete_results_dir()
        utils.create_results_dir()
        utils.delete_data_dir()
        utils.create_data_dir()

        if not g.pipeline_running:
            return

        # Run
        dtl_json = []
        postprocess_cb_list = []
        for node_id in nodes_state:
            node = g.layers.get(node_id)
            if node is None:
                sly.logger.debug(f"Node with id {node_id} is not found. Skipping...")
                continue
            dtl_json.append(node.to_json())
            postprocess_cb_list.append(node.postprocess_cb)

        g.current_dtl_json = dtl_json
        utils.save_dtl_json(dtl_json)

        if not g.pipeline_running:
            return

        net = compute_dtls(progress, circle_progress, g.MODALITY_TYPE, postprocess_cb_list)

        if not g.pipeline_running:
            return
        # Save results
        file_infos = []
        pr_dirs = []

        if os.path.exists(g.RESULTS_DIR):
            for pr_dir in os.listdir(g.RESULTS_DIR):
                pr_dir = os.path.join(g.RESULTS_DIR, pr_dir)
                if os.path.isdir(pr_dir):
                    pr_dirs.append(pr_dir)
        # pr_dirs = [p for p in Path(g.RESULTS_DIR).iterdir() if p.is_dir()]

        for i, pr_dir in enumerate(pr_dirs):
            pr_dir_name = os.path.basename(pr_dir)
            if not g.pipeline_running:
                return

            with progress(
                message=[f'[{i+1}/{len(pr_dirs)}] Archiving result project "{pr_dir_name}"'],
                total=1,
            ) as pbar:
                tar_path = str(pr_dir) + ".tar"
                sly.fs.archive_directory(pr_dir, tar_path)
                pbar.update(1)

            if not g.pipeline_running:
                return

            with progress(
                message=f'[{i+1}/{len(pr_dirs)}] Uploading result project "{pr_dir_name}"',
                unit="B",
                unit_scale=True,
                total=get_file_size(tar_path),
            ) as pbar:

                if not g.pipeline_running:
                    return

                if g.TASK_ID is not None:  # is production
                    dst = f"/{g.TEAM_FILES_PATH}/archives/{g.MODALITY_TYPE}/{g.TASK_ID}/{Path(tar_path).name}"
                else:  # is development
                    dst = (
                        f"/{g.TEAM_FILES_PATH}/archives/{g.MODALITY_TYPE}/DEV/{Path(tar_path).name}"
                    )
                if g.api.file.exists(g.TEAM_ID, dst):
                    dst = g.api.file.get_free_name(g.TEAM_ID, dst)

                if not g.pipeline_running:
                    return

                file_info = g.api.file.upload(
                    g.TEAM_ID,
                    src=tar_path,
                    dst=dst,
                    progress_cb=pbar,
                )

                if not g.pipeline_running:
                    return
            # delete after upload?

            file_infos.append(file_info)

            if not g.pipeline_running:
                return

            if not sly.is_development():
                g.api.task.set_output_archive(sly.env.task_id(), file_info.id, file_info.name)

            if not g.pipeline_running:
                return

        data_layers = [
            l
            for l in net.layers
            if isinstance(
                l,
                (
                    FilteredProjectLayer,
                    ImagesProjectLayer,
                    InputLabelingJobLayer,
                    VideosProjectLayer,
                ),
            )
        ]

        supervisely_layers = [
            l
            for l in net.layers
            if isinstance(
                l,
                (
                    CreateNewProjectLayer,
                    AddToExistingProjectLayer,
                    CopyAnnotationsLayer,
                    OutputProjectLayer,
                ),
            )
        ]

        if not g.pipeline_running:
            return

        labeling_job_layers = [l for l in net.layers if isinstance(l, CreateLabelingJobLayer)]

        # Outputs
        results.set_content(
            ui_utils.create_results_widget(file_infos, supervisely_layers, labeling_job_layers)
        )

        results.reload()
        results.show()
        circle_progress.set_status("success")

        # ---------------------------------------- Workflow ---------------------------------------------- #
        sly.logger.info(f"Workflow started. Workflow ID: {g.WORKFLOW_ID}")
        # ---------------------------------------- Workflow Input ---------------------------------------- #
        w.workflow_input(g.api, data_layers)
        # ----------------------------------------------- - ---------------------------------------------- #

        # ---------------------------------------- Workflow Output --------------------------------------- #
        w.workflow_output(
            g.api,
            project_layers=supervisely_layers,
            job_layers=labeling_job_layers,
            file_infos=file_infos,
        )
        sly.logger.info(f"Workflow finished.")
        # sly.logger.info(f"Workflow finished. Next workflow ID: {g.WORKFLOW_ID}")
        # ----------------------------------------------- - ---------------------------------------------- #

    except CustomException as e:
        g.disable_move = True
        error_notification.set(title="Error", description=str(e.args[0]))
        error_notification.show()
        circle_progress.set_status("exception")
        raise e
    except Exception as e:
        g.disable_move = True
        error_notification.set("Error", description=str(e))
        error_notification.show()
        circle_progress.set_status("exception")
        raise e

    finally:
        progress.hide()
        with progress(message="Ready for new pipeline", total=1) as pbar:
            pbar.update(1)

        stop_btn.hide()

        if error_notification.title == "Pipeline will be stopped":
            sly.logger.info("Pipeline was manually stopped. Results may be incomplete.")
            error_notification.set(
                "Pipeline was manually stopped", description="Results may be incomplete."
            )
        stop_btn.enable()
        run_btn.show()
        nodes_flow_card.unlock()
        g.warn_notification.hide()
        nodes_flow.enable()
        g.pipeline_running = False
        show_run_dialog_btn_running.hide()
        show_run_dialog_btn.show()
        g.pipeline_thread = None
        global_timer.dump()


def run_pipeline(run_dialog: Dialog = None):
    g.pipeline_running = True
    if run_dialog is not None:
        run_dialog.show()
    show_run_dialog_btn.hide()
    show_run_dialog_btn_running.show()
    try:
        _run()
    finally:
        g.pipeline_running = False
        show_run_dialog_btn_running.hide()
        show_run_dialog_btn.show()
        g.pipeline_thread = None


def start_pipeline(run_dialog: Dialog = None):
    g.current = 0
    g.total = 0
    if g.pipeline_thread is not None or g.pipeline_running is True:
        error_notification.set(
            title="Pipeline is already running",
            description="Please wait for it to finish or press Stop",
        )
        error_notification.show()
        sly.logger.warn("Pipeline is already running. Please wait for it to finish or press Stop")
        # raise RuntimeError("Pipeline is already running")
    else:
        g.pipeline_thread = threading.Thread(target=run_pipeline, args=(run_dialog,), daemon=True)
        g.pipeline_thread.start()


@run_btn.click
@handle_exception
def run_btn_clicked():
    start_pipeline()


@stop_btn.click
@handle_exception
def stop_pipeline():
    stop_btn.disable()
    if g.pipeline_thread is not None:
        if g.pipeline_thread.is_alive():
            g.pipeline_thread = None
            g.pipeline_running = False
            sly.logger.info("Pipeline will be stopped. Results may be incomplete.")
            error_notification.set(
                "Pipeline will be stopped", description="Results may be incomplete."
            )
            error_notification.show()
            circle_progress.hide()
            show_run_dialog_btn_running.hide()
            show_run_dialog_btn.show()
            # other settings are set in finally block of _run
    else:
        progress.hide()
        with progress(message="Ready for new pipeline", total=1) as pbar:
            pbar.update(1)
        stop_btn.hide()
        run_btn.show()
        nodes_flow_card.unlock()
        g.warn_notification.hide()
        nodes_flow.enable()
        g.pipeline_running = False
        show_run_dialog_btn_running.hide()
        show_run_dialog_btn.show()
        g.pipeline_thread = None
