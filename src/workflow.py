# This module contains the functions that are used to configure the input and output of the workflow for the current app.

import json
from os.path import join, dirname
from src.ui.tabs.configure import nodes_flow
import src.ui.utils as ui_utils
import src.utils as utils
import src.globals as g
from typing import Optional, List
import supervisely as sly

from supervisely.api.file_api import FileInfo
from supervisely.api.project_api import ProjectInfo
from supervisely.api.labeling_job_api import LabelingJobInfo
from src.compute.layers.data.InputLabelingJobLayer import InputLabelingJobLayer
from src.compute.layers import Layer
from supervisely.api.module_api import ApiField

is_input_processed = False
is_output_processed = False
input_project_infos = []


def workflow_input(api: sly.Api, data_layers: List[Layer]):
    global is_input_processed
    global input_project_infos
    if is_input_processed is False:
        try:
            input_project_names = [
                layer.project_name
                for layer in data_layers
                if not isinstance(layer, InputLabelingJobLayer)
            ]
            input_project_infos = g.api.project.get_list(
                g.WORKSPACE_ID,
                filters=[
                    {
                        ApiField.FIELD: ApiField.NAME,
                        ApiField.OPERATOR: "in",
                        ApiField.VALUE: input_project_names,
                    }
                ],
            )
            input_job_ids = [
                layer.settings.get("job_id", None)
                for layer in data_layers
                if isinstance(layer, InputLabelingJobLayer)
            ]
        except Exception as e:
            sly.logger.debug(f"Workflow: Failed to collect input data {repr(e)}")
        try:
            for info in input_project_infos:
                api.app.workflow.add_input_project(info.id)
                sly.logger.debug(f"Workflow: Input project - {info.id}")
        except Exception as e:
            sly.logger.debug(f"Workflow: Failed to add input projects to the workflow: {repr(e)}")
        try:
            for job_id in input_job_ids:
                if job_id is not None:
                    api.app.workflow.add_input_job(job_id)
                    sly.logger.debug(f"Workflow: Input labeling job - {job_id}")
        except Exception as e:
            sly.logger.debug(
                f"Workflow: Failed to add input labeling jobs to the workflow: {repr(e)}"
            )
        is_input_processed = True
    else:
        sly.logger.debug("Workflow: Input data has already been processed. Skipping.")


def upload_workflow_preset():
    edges = nodes_flow.get_edges_json()
    nodes_state = nodes_flow.get_nodes_state_json()
    nodes_json = nodes_flow.get_nodes_json()

    # save node order position
    scene_location = []
    for idx, node_json in enumerate(nodes_json):
        scene_location.append({"order_idx": idx, "position": node_json["position"]})

    # Init layers data
    layers_ids = ui_utils.init_layers(nodes_state)
    all_layers_ids = layers_ids["all_layers_ids"]
    ui_utils.init_src(edges)

    dtl_json = [g.layers[layer_id].to_json() for layer_id in all_layers_ids]
    for idx, layer_json in enumerate(dtl_json):
        layer_json["scene_location"] = scene_location[idx]

    preset_name = f"workflow_preset_{g.WORKFLOW_ID}"
    dst_path = f"{g.OFFLINE_SESSION_PATH}/{preset_name}.json"

    src_path = join(g.WORKFLOW_DIR, "/preset.json")
    utils.create_workflow_dir()
    with open(src_path, "w") as f:
        json.dump(dtl_json, f, indent=4)

    sly.logger.info(f"Workflow: Uploading preset file to: '{dst_path}'")
    file_info = g.api.file.upload(g.TEAM_ID, src_path, dst_path)
    sly.logger.info("Workflow: Preset file uploaded successfully")
    g.WORKFLOW_ID += 1
    return file_info


def workflow_output(
    api: sly.Api,
    project_layers: Optional[List[Layer]] = None,
    job_layers: Optional[List[Layer]] = None,
    file_infos: Optional[List[FileInfo]] = None,
):
    global is_output_processed
    global input_project_infos

    if is_output_processed is False:
        try:
            preset_file = upload_workflow_preset()

            project_infos: Optional[List[ProjectInfo]] = [
                layer.sly_project_info for layer in project_layers
            ]
            job_project_infos: Optional[List[ProjectInfo]] = [
                layer.sly_project_info for layer in job_layers
            ]
            project_infos.extend(job_project_infos)
            # --------------------------------------- Remove Duplicates -------------------------------------- #
            unique_project_infos = {project_info.id: project_info for project_info in project_infos}
            project_infos = list(unique_project_infos.values())
            # ------------------------------------- Remove Duplicates End ------------------------------------ #
            job_infos: Optional[List[LabelingJobInfo]] = [
                job for layer in job_layers for job in layer.created_labeling_jobs
            ]
        except Exception as e:
            sly.logger.debug(
                f"Workflow: Provided data for output is not valid or processed with errors: {repr(e)}"
            )

        try:
            if project_infos is not None and len(project_infos) > 0:
                for p_info in project_infos:
                    if p_info in input_project_infos:
                        sly.logger.debug(
                            f"Workflow: Skipping input project for output - {p_info.id}"
                        )
                        continue
                    api.app.workflow.add_output_project(p_info.id)
                    sly.logger.debug(f"Workflow: Output project - {p_info.id}")
        except Exception as e:
            sly.logger.debug(f"Workflow: Failed to add output projects to the workflow: {repr(e)}")
        try:
            if job_infos is not None and len(job_infos) > 0:
                for j_info in job_infos:
                    api.app.workflow.add_output_job(j_info.id)
                    sly.logger.debug(f"Workflow: Output labeling job - {j_info.id}")
        except Exception as e:
            sly.logger.debug(
                f"Workflow: Failed to add output labeling jobs to the workflow: {repr(e)}"
            )
        try:
            if file_infos is not None and len(file_infos) > 0:
                n = len(file_infos)
                folder_path = dirname(file_infos[0].path)
                relation_settings = sly.WorkflowSettings(
                    title=f"Project Archives ({n})",
                    icon="archive",
                    icon_color="#ff4c9e",
                    icon_bg_color="#ffe3ed",
                )
                meta = sly.WorkflowMeta(relation_settings=relation_settings)
                api.app.workflow.add_output_folder(folder_path, meta=meta)
                sly.logger.debug(f"Workflow: Output folder with project archives - {file_infos[0]}")
        except Exception as e:
            sly.logger.debug(
                f"Workflow: Failed to add output folder with project archives to the workflow: {repr(e)}"
            )
        try:
            if preset_file is not None:
                relation_settings = sly.WorkflowSettings(
                    title=f"Workflow Preset",
                    icon="view-dashboard",
                    icon_color="#ffffff",
                    icon_bg_color="#cdcce3",
                    url=f"/files/{preset_file.id}/true/?teamId={preset_file.team_id}",
                    url_title="Show Preset",
                )
                meta = sly.WorkflowMeta(relation_settings=relation_settings)
                api.app.workflow.add_output_file(preset_file, meta=meta)
                sly.logger.debug(f"Workflow: Output preset file - {preset_file}")
        except Exception as e:
            sly.logger.debug(
                f"Workflow: Failed to add output preset file to the workflow: {repr(e)}"
            )
        is_output_processed = True
    else:
        sly.logger.debug("Workflow: Output data has already been processed. Skipping.")
