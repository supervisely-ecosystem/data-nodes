# coding: utf-8

from typing import List, Optional

from src.utils import get_project_by_name
import src.globals as g

# Action types whose "src" holds ["project_name/dataset_name", ...], same as images_project.
_NAMED_SOURCE_ACTIONS = ("images_project", "videos_project", "input_labeling_job")


def get_action_project_id(action: dict) -> Optional[int]:
    """Return the project id a single DTL input-layer action reads from, or None if this
    action type isn't a recognized project source."""
    action_type = action.get("action")
    if action_type in _NAMED_SOURCE_ACTIONS:
        src = action.get("src") or []
        if len(src) == 0:
            return None
        project_name = src[0].split("/")[0]
        return get_project_by_name(project_name).id
    if action_type == "filtered_project":
        return (action.get("settings") or {}).get("project_id")
    return None


def get_source_project_ids_from_dtl() -> List[int]:
    """Collect the project id of every recognized input-layer action in the current pipeline."""
    source_projects_ids = []
    for action in g.current_dtl_json:
        project_id = get_action_project_id(action)
        if project_id is not None:
            source_projects_ids.append(project_id)
    return source_projects_ids
