from pathlib import Path

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
from src.compute.layers.save.SuperviselyLayer import SuperviselyLayer
from src.compute.layers.save.ExistingProjectLayer import ExistingProjectLayer
from src.compute.layers.save.LabelingJobLayer import LabelingJobLayer
from src.ui.tabs.configure import nodes_flow
import src.utils as utils
import src.ui.utils as ui_utils
import src.globals as g
from src.exceptions import CustomException, handle_exception
from src.ui.widgets import CircleProgress
import threading
import multiprocessing

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
    widgets=[run_btn, stop_btn, progress, error_notification, download_archives_urls, results]
)


def _run():
    run_btn.hide()
    stop_btn.show()

    circle_progress.set_status("none")
    circle_progress.show()

    error_notification.hide()

    if not g.running_pipeline:
        return

    edges = nodes_flow.get_edges_json()
    nodes_state = nodes_flow.get_nodes_state_json()

    run_btn.hide()
    results.hide()
    progress(message="Running...", total=1)
    progress.show()

    try:
        # init layers
        ui_utils.init_layers(nodes_state)

        # init layers sources
        # destinations are defined in init_layers
        ui_utils.init_src(edges)

        if not g.running_pipeline:
            return

        # prepare results dir
        utils.delete_results_dir()
        utils.create_results_dir()
        utils.delete_data_dir()
        utils.create_data_dir()

        if not g.running_pipeline:
            return

        # Run
        dtl_json = [g.layers[node_id].to_json() for node_id in nodes_state]
        g.current_dtl_json = dtl_json
        utils.save_dtl_json(dtl_json)

        if not g.running_pipeline:
            return

        net = compute_dtls(progress, g.MODALITY_TYPE)

        if not g.running_pipeline:
            return
        # Save results
        file_infos = []
        pr_dirs = [p for p in Path(g.RESULTS_DIR).iterdir() if p.is_dir()]
        for i, pr_dir in enumerate(pr_dirs):

            if not g.running_pipeline:
                return

            with progress(
                message=[f'[{i+1}/{len(pr_dirs)}] Archiving result project "{pr_dir.name}"'],
                total=1,
            ) as pbar:
                tar_path = str(pr_dir) + ".tar"
                sly.fs.archive_directory(pr_dir, tar_path)
                pbar.update(1)

            if not g.running_pipeline:
                return

            with progress(
                message=f'[{i+1}/{len(pr_dirs)}] Uploading result project "{pr_dir.name}"',
                unit="B",
                unit_scale=True,
                total=get_file_size(tar_path),
            ) as pbar:

                if not g.running_pipeline:
                    return

                dst = f"/{g.TEAM_FILES_PATH}/archives/{g.MODALITY_TYPE}/{Path(tar_path).name}"
                if g.api.file.exists(g.TEAM_ID, dst):
                    dst = g.api.file.get_free_name(g.TEAM_ID, dst)

                if not g.running_pipeline:
                    return

                file_info = g.api.file.upload(
                    g.TEAM_ID,
                    src=tar_path,
                    dst=dst,
                    progress_cb=pbar,
                )

                if not g.running_pipeline:
                    return
            # delete after upload?

            file_infos.append(file_info)

            if not g.running_pipeline:
                return

            if not sly.is_development():
                g.api.task.set_output_archive(sly.env.task_id(), file_info.id, file_info.name)

            if not g.running_pipeline:
                return

        supervisely_layers = [
            l for l in net.layers if isinstance(l, (SuperviselyLayer, ExistingProjectLayer))
        ]

        if not g.running_pipeline:
            return

        labeling_job_layers = [l for l in net.layers if isinstance(l, LabelingJobLayer)]
        results.set_content(
            ui_utils.create_results_widget(file_infos, supervisely_layers, labeling_job_layers)
        )

        results.reload()
        results.show()
        circle_progress.set_status("success")
    except CustomException as e:
        error_notification.set(title="Error", description=str(e))
        error_notification.show()
        circle_progress.set_status("exception")
        raise e
    except Exception as e:
        error_notification.set("Error", description=str(e))
        error_notification.show()
        circle_progress.set_status("exception")
        raise e
    finally:
        progress.hide()
        run_btn.show()
        stop_btn.hide()


def run_pipeline():
    while g.running_pipeline:
        _run()
        g.running_pipeline = False
        g.pipeline_thread = None


@run_btn.click
@handle_exception
def start_pipeline():
    if g.pipeline_thread is not None:
        raise RuntimeError("Pipeline is already running")
    g.running_pipeline = True
    g.pipeline_thread = threading.Thread(target=run_pipeline, daemon=True)
    g.pipeline_thread.start()


@stop_btn.click
@handle_exception
def stop_pipeline():
    if g.pipeline_thread.is_alive():
        g.pipeline_thread = None
        g.running_pipeline = False
        sly.logger.info("Pipeline was manually stopped. Results may be incomplete.")
        error_notification.set(
            "Pipeline was manually stopped", description="Results may be incomplete."
        )
        error_notification.show()
        circle_progress.hide()
        stop_btn.hide()
        run_btn.show()
