from pathlib import Path
import os

from supervisely.app.widgets import (
    Button,
    Container,
    Progress,
    Text,
    ReloadableArea,
    Empty,
    NotificationBox,
)
from supervisely.io.fs import get_file_size
import supervisely as sly

from src.compute.main import main as compute_dtls
from src.compute.layers.save.CreateNewProjectLayer import CreateNewProjectLayer
from src.compute.layers.save.AddToExistingProjectLayer import AddToExistingProjectLayer
from src.compute.layers.save.CopyAnnotationsLayer import CopyAnnotationsLayer
from src.compute.layers.save.CreateLabelingJobLayer import CreateLabelingJobLayer
from src.ui.tabs.configure import nodes_flow, nodes_flow_card
import src.utils as utils
import src.ui.utils as ui_utils
import src.globals as g
from src.exceptions import CustomException, handle_exception
from src.ui.widgets import CircleProgress
import threading

show_run_dialog_btn = Button(
    "Run",
    icon="zmdi zmdi-play",
    button_size="small",
    style="border: 1px solid rgb(191, 203, 217); margin: 10px 0px 0px 25px; padding: 9px 13px; border-radius: 6px; font-size: 12px; text-transform: uppercase; font-weight: 500; background-color: #448dff; color: white; border-color: transparent; height: 32px;",
)
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

    edges = nodes_flow.get_edges_json()
    nodes_state = nodes_flow.get_nodes_state_json()

    run_btn.hide()
    results.hide()
    progress(message="Validating...", total=1)
    progress.show()

    try:
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
        dtl_json = [g.layers[node_id].to_json() for node_id in nodes_state]
        postprocess_cb_list = [g.layers[node_id].postprocess_cb for node_id in nodes_state]

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

                dst = f"/{g.TEAM_FILES_PATH}/archives/{g.MODALITY_TYPE}/{Path(tar_path).name}"
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

        supervisely_layers = [
            l
            for l in net.layers
            if isinstance(
                l, (CreateNewProjectLayer, AddToExistingProjectLayer, CopyAnnotationsLayer)
            )
        ]

        if not g.pipeline_running:
            return

        labeling_job_layers = [l for l in net.layers if isinstance(l, CreateLabelingJobLayer)]
        results.set_content(
            ui_utils.create_results_widget(file_infos, supervisely_layers, labeling_job_layers)
        )

        results.reload()
        results.show()
        circle_progress.set_status("success")
    except CustomException as e:
        error_notification.set(title="Error", description=str(e.args[0]))
        error_notification.show()
        circle_progress.set_status("exception")
        raise e
    except Exception as e:
        error_notification.set("Error", description=str(e))
        error_notification.show()
        circle_progress.set_status("exception")
        raise e

    finally:
        g.pipeline_running = False
        g.pipeline_thread = None
        g.warn_notification.hide()
        nodes_flow.enable()
        progress.hide()
        with progress(message="Ready for new pipeline", total=1) as pbar:
            pbar.update(1)

        stop_btn.hide()
        run_btn.show()
        nodes_flow_card.unlock()


def run_pipeline():
    while g.pipeline_running:
        _run()
        g.pipeline_running = False
        g.pipeline_thread = None


@run_btn.click
@handle_exception
def start_pipeline():
    if g.pipeline_thread is not None:
        raise RuntimeError("Pipeline is already running")
    g.pipeline_running = True
    g.pipeline_thread = threading.Thread(target=run_pipeline, daemon=True)
    g.pipeline_thread.start()


@stop_btn.click
@handle_exception
def stop_pipeline():
    if g.pipeline_thread.is_alive():
        g.pipeline_thread = None
        g.pipeline_running = False
        sly.logger.info("Pipeline was manually stopped. Results may be incomplete.")
        error_notification.set(
            "Pipeline was manually stopped", description="Results may be incomplete."
        )
        error_notification.show()
        circle_progress.hide()
        # other settings are set in finally block of _run
