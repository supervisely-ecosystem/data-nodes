from typing import Optional

import supervisely.io.env as sly_env
from supervisely.app import StateJson, DataJson
from supervisely.app.widgets import Widget
from supervisely.api.api import Api
from supervisely.api.labeling_job_api import LabelingJobInfo


class LabelingJobInfoWidget(Widget):
    def __init__(
        self,
        team_id: int = None,
        job_id: int = None,
        job_info: LabelingJobInfo = None,
        widget_id: str = None,
    ):
        self._api = Api()
        self._job_id = job_id
        self._team_id = team_id
        self._job_info = None
        if job_info is not None:
            self._job_info = self._convert_to_json(job_info)

        if self._team_id is None:
            self._team_id = sly_env.team_id()

        super().__init__(widget_id=widget_id, file_path=__file__)

    def get_json_data(self):
        data = {}
        data["teamId"] = self._team_id
        if self._job_id is not None:
            if self._job_info is None:
                data["job_info"] = self._get_info()
            else:
                data["job_info"] = self._job_info
        elif self._job_id is None and self._job_info is not None:
            data["job_info"] = self._job_info
        else:
            data["job_info"] = None
        return data

    def get_json_state(self):
        state = {}
        state["jobId"] = self._job_id
        return state

    def set_id(self, job_id: int):
        self._job_id = job_id
        self._job_info = self._get_info()
        self.update_data()
        self.update_state()
        DataJson().send_changes()
        StateJson().send_changes()

    def set_info(
        self,
        job_id: Optional[int] = None,
        job_info: Optional[LabelingJobInfo] = None,
    ):
        if job_id is None and job_info is None:
            raise ValueError("Both job_id and job_info can't be None.")

        if job_info is None:
            job_info = self._get_info()
        if isinstance(job_info, LabelingJobInfo):
            job_info = self._convert_to_json(job_info)

        self._job_id = job_id
        self._job_info = job_info
        self.update_data()
        self.update_state()
        DataJson().send_changes()
        StateJson().send_changes()

    def _get_info(self) -> LabelingJobInfo:
        job_info = self._api.labeling_job.get_info_by_id(self._job_id)
        self._job_info = self._convert_to_json(job_info)
        return self._job_info

    def _convert_to_json(self, job_info: LabelingJobInfo):
        job_status = None
        if job_info.status == "pending":
            job_status = "Pending"
        elif job_info.status == "in_progress":
            job_status = "In progress"
        elif job_info.status == "on_review":
            job_status = "On review"
        elif job_info.status == "completed":
            job_status = "Completed"
        elif job_info.status == "stopped":
            job_status = "Stopped"

        return {
            "Job ID": job_info.id,
            "Job name": job_info.name,
            "Job status": job_status,
            "Job owner": job_info.created_by_login,
            "Labeler": job_info.assigned_to_login,
            "Reviewer": job_info.reviewer_login,
            "Project name": job_info.project_name,
            "Project ID": job_info.project_id,
            "Dataset name": job_info.dataset_name,
            "Dataset ID": job_info.dataset_id,
            "Classes to label": len(job_info.classes_to_label),
            "Tags to label": len(job_info.tags_to_label),
            "Images count": job_info.images_count,
            "Finished images count": job_info.finished_images_count,
        }

    @property
    def job_id(self):
        return self._job_id
