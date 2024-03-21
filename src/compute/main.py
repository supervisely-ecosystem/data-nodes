# coding: utf-8

import os

import supervisely as sly
from supervisely import sly_logger
from supervisely.app.widgets.sly_tqdm.sly_tqdm import Progress
from src.ui.widgets import CircleProgress
from supervisely.sly_logger import logger, EventType

from src.compute.dtl_utils.dtl_helper import DtlHelper, DtlPaths
from src.compute.tasks import task_helpers
from src.compute.utils import logging_utils
from src.compute.Net import Net
from src.exceptions import CustomException, GraphError
from src.utils import LegacyProjectItem
import src.globals as g
from time import time


def make_legacy_project_item(project: sly.Project, dataset, item_name):
    item_name_base, item_ext = os.path.splitext(item_name)
    return LegacyProjectItem(
        project_name=project.name,
        ds_name=dataset.name,
        item_name=item_name_base,
        item_info=None,
        ia_data={"item_ext": item_ext},
        item_path=dataset.get_img_path(item_name),
        ann_path=dataset.get_ann_path(item_name),
    )


def check_in_graph():
    helper = DtlHelper()
    net = Net(helper.graph, helper.in_project_metas, helper.paths.results_dir, helper.modality)
    net.validate()
    net.calc_metas()

    need_download = net.may_require_items()
    return {"download_items": need_download}


def calculate_datasets_conflict_map(helper):
    tmp_datasets_map = {}

    # Save all [datasets : projects] relations
    for _, pr_dir in helper.in_project_dirs.items():
        project = sly.Project(directory=pr_dir, mode=sly.OpenMode.READ)
        for dataset in project:
            projects_list = tmp_datasets_map.setdefault(dataset.name, [])
            projects_list.append(project.name)

    datasets_conflict_map = {}
    for dataset_name in tmp_datasets_map:
        projects_names_list = tmp_datasets_map[dataset_name]
        for project_name in projects_names_list:
            datasets_conflict_map[project_name] = datasets_conflict_map.get(project_name, {})
            datasets_conflict_map[project_name][dataset_name] = len(projects_names_list) > 1

    return datasets_conflict_map


def main(
    progress: Progress,
    circle_progress: CircleProgress,
    modality: str,
    postprocess_cb_list: list = None,
):
    total_pipeline_time_start = time()
    task_helpers.task_verification(check_in_graph)

    if not g.pipeline_running:
        return

    logger.info("DTL started")
    helper = DtlHelper()

    try:
        net = Net(helper.graph, helper.paths.results_dir, modality)

        if postprocess_cb_list is not None:
            for layer, postprocess_cb in zip(net.layers, postprocess_cb_list):
                layer.postprocess_cb = postprocess_cb

        validation_time_start = time()

        try:
            net.validate(circle_progress)
        except:
            circle_progress.hide()
            raise

        validation_time_end = time()
        logger.debug(
            f"Total validation time: {validation_time_end-validation_time_start:.10f} seconds."
        )

        net.calc_metas()

        if not g.pipeline_running:
            return

        net.preprocess()

        if not g.pipeline_running:
            return

        datasets_conflict_map = calculate_datasets_conflict_map(helper)

        if not g.pipeline_running:
            return

    except CustomException as e:
        circle_progress.hide()
        # logger.error("Error occurred on DTL-graph initialization step!")
        # e.log()
        raise e
    except Exception as e:
        circle_progress.hide()
        # logger.error("Error occurred on DTL-graph initialization step!", exc_info=str(e))
        raise e

    total = net.get_total_elements()
    if total == 0:
        raise GraphError(
            "There are no elements to process. Make sure that you selected input project"
        )
    elements_generator = net.get_elements_generator()

    if not g.pipeline_running:
        return

    results_counter = 0
    processing_time_start = time()
    with progress(message=f"Processing items...", total=total) as pbar:
        for data_el in elements_generator:
            start_item_processing_time = time()
            try:
                export_output_generator = net.start(data_el)
                if not g.pipeline_running:
                    return
                for res_export in export_output_generator:
                    if not g.pipeline_running:
                        return
                    logger.trace(
                        "item processed",
                        extra={"item_name": res_export[0][0].get_item_name()},
                    )
                    results_counter += 1
            except Exception as e:
                extra = {
                    "project_name": data_el[0].get_pr_name(),
                    "ds_name": data_el[0].get_ds_name(),
                    "item_name": data_el[0].get_item_name(),
                    "exc_str": str(e),
                }
                logger.warn(
                    "Item was skipped because some error occurred",
                    exc_info=True,
                    extra=extra,
                )
            finally:
                end_item_processing_time = time()
                logger.debug(
                    f"{data_el[0].info.item_info.name} processing time: {end_item_processing_time - start_item_processing_time:.10f} seconds."
                )
                pbar.update()

    processing_time_end = time()
    logger.debug(
        f"Total items processing time: {processing_time_end-processing_time_start:.10f} seconds."
    )
    if not g.pipeline_running:
        return

    postprocessing_time_start = time()
    net.postprocess()
    postprocessing_time_end = time()
    logger.debug(
        f"Total postprocessing time: {postprocessing_time_end-postprocessing_time_start:.10f} seconds."
    )

    if not g.pipeline_running:
        return

    logger.info(
        "DTL finished",
        extra={"event_type": EventType.DTL_APPLIED, "new_proj_size": results_counter},
    )
    total_pipeline_time_end = time()
    logger.info(
        f"Total pipeline time: {total_pipeline_time_end-total_pipeline_time_start:.10f} seconds."
    )
    return net


if __name__ == "__main__":
    if os.getenv("DEBUG_LOG_TO_FILE", None):
        sly_logger.add_default_logging_into_file(logger, DtlPaths().debug_dir)
    logging_utils.main_wrapper("DTL", main)
