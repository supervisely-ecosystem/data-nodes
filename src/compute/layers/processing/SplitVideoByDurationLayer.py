# coding: utf-8

from os.path import join, splitext
from typing import Tuple, List
from copy import deepcopy

from supervisely import (
    VideoAnnotation,
    Frame,
    FrameCollection,
    VideoTagCollection,
)
from supervisely.api.video.video_api import VideoInfo
from src.utils import LegacyProjectItem

from src.compute.Layer import Layer
from src.compute.dtl_utils.item_descriptor import VideoDescriptor
from moviepy.video.io.VideoFileClip import VideoFileClip
from supervisely.io.fs import get_file_name, get_file_ext

from supervisely.video.video import get_info as get_video_info

import src.globals as g


# Split functions


def get_time_splitter(split_sec, video_length):
    splitter = []
    full_parts = int(video_length // split_sec)

    i = None
    for i in range(full_parts):
        splitter.append([split_sec * i, split_sec * (i + 1)])
    splitter.append([split_sec * (i + 1), video_length + 0.001])
    return splitter


def get_frames_splitter(split_frames, fr_to_timecodes):
    splitter = []
    for start in range(0, len(fr_to_timecodes), split_frames):
        end = min(start + split_frames - 1, len(fr_to_timecodes) - 1)
        splitter.append([fr_to_timecodes[start], fr_to_timecodes[end] + 0.001])
    return splitter


def write_videos(video_path: str, splitter: list, result_dir: str, video_info: VideoInfo) -> tuple:
    curr_video_paths = []
    curr_video_names = []
    for idx, curr_split in enumerate(splitter):
        with VideoFileClip(video_path) as video:
            new_video = video.subclip(curr_split[0], curr_split[1])
            split_video_name = (
                f"{get_file_name(video_info.name)}_{str(idx + 1)}{get_file_ext(video_info.name)}"
            )
            output_video_path = join(result_dir, split_video_name)
            curr_video_names.append(split_video_name)
            curr_video_paths.append(output_video_path)
            new_video.write_videofile(output_video_path, audio_codec="aac")
    return curr_video_paths, curr_video_names


def get_ann_tags(ann: VideoAnnotation) -> tuple:
    video_tags = []
    frame_range_tags = []
    for tag in ann.tags:
        if tag.frame_range is None:
            video_tags.append(tag)
        else:
            frame_range_tags.append(tag)
    return video_tags, frame_range_tags


def get_frame_range_tags(frame_range_tags, curr_frame_range):
    result_tags = []
    curr_fr_range = list(range(curr_frame_range[0], curr_frame_range[1]))
    for tag in frame_range_tags:
        fr_range = list(range(tag.frame_range[0], tag.frame_range[1] + 1))
        res = list(set(fr_range) & set(curr_fr_range))
        if len(res) == 0:
            continue
        result_tags.append(
            tag.clone(
                frame_range=[min(res) - curr_frame_range[0], max(res) - curr_frame_range[0]],
                key=tag.key(),
            )
        )
    return result_tags


def get_new_frames(old_frames: List[Frame]) -> FrameCollection:
    new_frames = []
    for index, frame in enumerate(old_frames):
        new_figures = []
        for figure in frame.figures:
            new_figure = figure.clone(frame_index=index)
            new_figures.append(new_figure)
        new_frame = frame.clone(index=index, figures=new_figures)
        new_frames.append(new_frame)
    split_frames = FrameCollection(new_frames)
    return split_frames


def process_annotations(
    video_splits_paths: List[str], ann: VideoAnnotation
) -> List[VideoAnnotation]:  #  video_splits_paths == new_video_infos
    video_tags, frame_range_tags = get_ann_tags(ann)
    ann_frames = ann.frames.items()
    video_infos = [get_video_info(video_path) for video_path in video_splits_paths]
    start_frames_count = video_infos[0]["streams"][0]["framesCount"]

    annotations = []
    for idx in range(len(video_infos)):
        curr_frames_count = video_infos[idx]["streams"][0]["framesCount"]

        curr_frame_range = [start_frames_count * idx, start_frames_count * (idx + 1)]
        split_ann_tags = deepcopy(video_tags)

        if start_frames_count * (idx + 1) > len(ann.frames):
            old_frames = ann_frames[start_frames_count * idx : len(ann.frames)]
        else:
            old_frames = ann_frames[start_frames_count * idx : curr_frames_count * (idx + 1)]

        split_frames_coll = get_new_frames(old_frames)
        range_tags = get_frame_range_tags(frame_range_tags, curr_frame_range)

        split_ann_tags.extend(range_tags)
        split_ann = ann.clone(
            frames_count=len(split_frames_coll),
            frames=split_frames_coll,
            tags=VideoTagCollection(split_ann_tags),
        )

        annotations.append(split_ann)
    return annotations


# unsafe method
def make_new_video_info(video_info: VideoInfo, video_name: str, video_path: str) -> VideoInfo:
    video = get_video_info(video_path)
    file_meta = video_info.file_meta
    file_meta["duration"] = video["duration"]
    file_meta["size"] = video["size"]
    file_meta["streams"] = video["streams"]
    for stream in video["streams"]:
        codec_type = stream.get("codec_type", None)
        if codec_type is None:
            codec_type = stream.get("codecType", None)
        if codec_type == "video":
            file_meta["framesCount"] = stream["framesCount"]
            file_meta["framesToTimecodes"] = stream["framesToTimecodes"]
            file_meta["height"] = stream["height"]
            file_meta["width"] = stream["width"]
            break

    new_video_info = VideoInfo(
        id=None,
        name=video_name,
        hash=None,
        link=None,
        team_id=g.TEAM_ID,
        workspace_id=g.WORKSPACE_ID,
        project_id=None,
        dataset_id=None,
        path_original=None,
        frames_to_timecodes=file_meta["framesToTimecodes"],
        frames_count=file_meta["framesCount"],
        frame_width=file_meta["width"],
        frame_height=file_meta["height"],
        created_at=None,
        updated_at=None,
        tags=video_info.tags,
        file_meta=file_meta,
        meta=None,
        custom_data={},
        processing_path=None,
    )
    return new_video_info


def process_splits(
    vid_desc: VideoDescriptor,
    video_path: str,
    video_name: str,
    ann: VideoAnnotation,
    video_info: VideoInfo,
):
    video_name, item_ext = splitext(video_name)
    vid_desc = VideoDescriptor(
        LegacyProjectItem(
            project_name=vid_desc.get_pr_name(),
            ds_name=vid_desc.get_ds_name(),
            item_name=video_name,
            item_info=video_info,
            ia_data={"item_ext": item_ext},
            item_path=video_path,
            ann_path="",
        ),
        False,
    )
    vid_desc.update_item(video_path)
    return vid_desc, ann


# -----------------


class SplitVideobyDurationLayer(Layer):
    action = "split_video_by_duration"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["duration_unit", "split_step"],
                "properties": {
                    "duration_unit": {
                        "type": "string",
                        "enum": [
                            "frames",
                            "seconds",
                        ],
                    },
                    "split_step": {"type": "integer", "minimum": 0},
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def modifies_data(self):
        return True

    def process(self, data_el: Tuple[VideoDescriptor, VideoAnnotation]):
        vid_desc, ann = data_el
        ann: VideoAnnotation

        duration_unit = self.settings["duration_unit"]
        split_step = self.settings["split_step"]
        video_info: VideoInfo = vid_desc.info.item_info

        if not self.net.preview_mode:
            video_frames_count = video_info.frames_count
            video_length = video_info.frames_to_timecodes[-1]
            if duration_unit == "frames":
                if split_step >= video_frames_count:
                    # Frames count set for splitting, is more then video
                    yield (vid_desc, ann)
                else:
                    splitter = get_frames_splitter(split_step, video_info.frames_to_timecodes)
                    video_splits_paths, video_splits_names = write_videos(
                        vid_desc.item_data, splitter, g.RESULTS_DIR, video_info
                    )
                    annotations = process_annotations(video_splits_paths, ann)
                    for video_path, video_name, ann in zip(
                        video_splits_paths, video_splits_names, annotations
                    ):
                        new_video_info = make_new_video_info(video_info, video_name, video_path)
                        yield process_splits(vid_desc, video_path, video_name, ann, new_video_info)

            else:
                if split_step >= video_info.duration:
                    # Time set for splitting, is more then video
                    yield (vid_desc, ann)
                else:
                    splitter = get_time_splitter(split_step, video_length)
                    video_splits_paths, video_splits_names = write_videos(
                        vid_desc.item_data, splitter, g.RESULTS_DIR, video_info
                    )

                    annotations = process_annotations(video_splits_paths, ann)

                    for video_path, video_name, ann in zip(
                        video_splits_paths, video_splits_names, annotations
                    ):
                        new_video_info = make_new_video_info(video_info, video_name, video_path)
                        yield process_splits(vid_desc, video_path, video_name, ann, new_video_info)
        else:
            yield vid_desc, ann
