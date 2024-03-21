from typing import List
from supervisely.app.widgets import (
    Button,
    Container,
    Text,
    Field,
    Select,
    DatasetThumbnail,
)
from src.ui.widgets import ClassesListPreview, LabelingJobInfoWidget, TagsListPreview
from src.ui.dtl.utils import (
    get_set_settings_button_style,
    get_set_settings_container,
    get_text_font_size,
)

from supervisely.api.labeling_job_api import LabelingJobInfo
import src.globals as g


def create_lj_selector_widgets() -> tuple:
    # SIDEBAR
    labeling_jobs: List[LabelingJobInfo] = g.api.labeling_job.get_list(g.TEAM_ID)

    lj_selector_sidebar_items_items = [
        Select.Item(value=job.id, label=job.name) for job in labeling_jobs
    ]
    lj_selector_sidebar_selector = Select(
        lj_selector_sidebar_items_items, placeholder="Select Labeling Job"
    )

    lj_selector_sidebar_selector_field = Field(
        title="Select Labeling Job",
        description="Select Labeling Job to use as input data",
        content=lj_selector_sidebar_selector,
    )

    if len(labeling_jobs) == 0:
        lj_selector_sidebar_lj_info = Text(
            "No Labeling Jobs found. Create Labeling job and create new 'Input Labeling Job' layer",
            status="warning",
            font_size=get_text_font_size(),
        )
    else:
        lj_selector_sidebar_lj_info = LabelingJobInfoWidget(
            g.TEAM_ID, labeling_jobs[0].id, labeling_jobs[0]
        )
    lj_selector_sidebar_lj_info_field = Field(
        title="Labeling Job Info",
        description="Information about selected Labeling Job",
        content=lj_selector_sidebar_lj_info,
    )

    lj_selector_sidebar_save_btn = Button(
        "Save", icon="zmdi zmdi-floppy", emit_on_click="save", call_on_click="closeSidebar();"
    )

    lj_selector_sidebar_container = Container(
        widgets=[
            lj_selector_sidebar_selector_field,
            lj_selector_sidebar_lj_info_field,
            lj_selector_sidebar_save_btn,
        ]
    )
    # --------------------------

    # PREVIEW
    lj_selector_preview_lj_text = Text(
        "Select Labeling Job to display info", status="text", font_size=get_text_font_size()
    )
    lj_selector_preview_lj_status = Text(font_size=get_text_font_size())
    lj_selector_preview_lj_status.hide()
    lj_selector_preview_lj_progress = Text(font_size=get_text_font_size())
    lj_selector_preview_lj_progress.hide()
    lj_selector_preview_lj_dataset_thumbnail = DatasetThumbnail()
    lj_selector_preview_lj_dataset_thumbnail.hide()

    lj_selector_preview_classes_text = Text(
        "Classes: 0 / 0", status="text", font_size=get_text_font_size()
    )
    lj_selector_preview_classes = ClassesListPreview(empty_text="Job has no classes to label")
    lj_selector_preview_tags_text = Text(
        "Tags: 0 / 0", status="text", font_size=get_text_font_size()
    )
    lj_selector_preview_tags = TagsListPreview(empty_text="Job has no tags to label")
    # --------------------------

    # LAYOUT
    lj_selector_layout_text = Text(
        "Select Labeling Job", status="text", font_size=get_text_font_size()
    )
    lj_selector_layout_btn = Button(
        text="SELECT",
        icon="zmdi zmdi-folder",
        button_type="text",
        button_size="small",
        emit_on_click="openSidebar",
        style=get_set_settings_button_style(),
    )
    lj_selector_layout_container = get_set_settings_container(
        lj_selector_layout_text, lj_selector_layout_btn
    )
    # --------------------------
    return (
        # sidebar
        lj_selector_sidebar_selector,
        lj_selector_sidebar_selector_field,
        lj_selector_sidebar_lj_info,
        lj_selector_sidebar_lj_info_field,
        lj_selector_sidebar_save_btn,
        lj_selector_sidebar_container,
        # preview
        lj_selector_preview_lj_text,
        lj_selector_preview_lj_status,
        lj_selector_preview_lj_progress,
        lj_selector_preview_lj_dataset_thumbnail,
        lj_selector_preview_classes_text,
        lj_selector_preview_classes,
        lj_selector_preview_tags_text,
        lj_selector_preview_tags,
        # layout
        lj_selector_layout_text,
        lj_selector_layout_btn,
        lj_selector_layout_container,
    )
