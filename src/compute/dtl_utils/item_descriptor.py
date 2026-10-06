# coding: utf-8

import os
import threading

from src.utils import LegacyProjectItem
import cv2
import numpy as np

from src.compute.utils.os_utils import ensure_base_path


class ItemDescriptor:

    def __init__(self, info: LegacyProjectItem, item_idx: int, modify_ds_name: bool = True):
        self.info = info
        self.item_data = None  # can be changed in comp graph
        self.item_idx = item_idx
        if modify_ds_name:
            self.res_ds_name = "{}__{}".format(self.info.project_name, self.info.ds_name)
        else:
            self.res_ds_name = self.info.ds_name

    def read_item(self) -> None:
        raise NotImplementedError

    def update_item(self, item) -> None:
        self.item_data = item

    # def write_item_local(self, item_path) -> None:
    #     raise NotImplementedError

    # def encode_item(self) -> None:
    #     raise NotImplementedError

    def get_item_idx(self) -> int:
        return self.item_idx

    def update_item_info(self, item_info: LegacyProjectItem) -> None:
        self.info.item_info = item_info

    def need_write(self) -> bool:
        if self.item_data is None:
            return False
        return True

    def get_res_ds_name(self) -> str:
        return self.res_ds_name

    def get_pr_name(self) -> str:
        return self.info.project_name

    def get_ds_name(self) -> str:
        return self.info.ds_name

    def get_ds_info(self) -> str:
        return self.info.ds_info

    def set_ds_info(self, new_ds_info) -> None:
        self.info.ds_info = new_ds_info

    def get_item_name(self) -> str:
        return self.info.item_name

    def get_item_ext(self) -> str:
        return self.info.ia_data["item_ext"]

    def get_item_path(self) -> str:
        return self.info.item_path

    def set_item_name(self, new_name) -> None:
        self.info.item_name = new_name

    def clone_with_item(self, new_item):
        new_obj = self.__class__(self.info, self.item_idx)
        new_obj.item_data = new_item
        new_obj.res_ds_name = self.res_ds_name
        return new_obj

    def clone_with_name(self, new_name) -> None:
        self.info: LegacyProjectItem
        new_info = self.info._replace(item_name=new_name)
        new_obj = self.__class__(new_info, self.item_idx)
        new_obj.item_data = self.item_data
        new_obj.res_ds_name = self.res_ds_name
        return new_obj


class ImageDescriptor(ItemDescriptor):

    def __init__(self, info: LegacyProjectItem, item_idx: int, modify_ds_name: bool = True) -> None:
        super().__init__(info, item_idx, modify_ds_name)

    def read_image(self) -> np.ndarray:
        if self.item_data is not None:
            return self.item_data

        img = cv2.imread(self.info.item_path)
        if img is None:
            raise RuntimeError("Image not found. {}".format(self.info.item_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    def write_image_local(self, img_path) -> None:
        if self.item_data is None:
            raise RuntimeError(
                "ImageDescriptor [write_image_local] item_data is None:{}".format(img_path)
            )
        img_res = self.item_data.astype(np.uint8)
        img_res = cv2.cvtColor(img_res, cv2.COLOR_RGB2BGR)
        ensure_base_path(img_path)
        cv2.imwrite(img_path, img_res)

    def encode_image(self) -> bytes:
        if self.item_data is None:
            raise RuntimeError("ImageDescriptor [encode_image] item_data is None.")
        img_res = self.item_data.astype(np.uint8)
        img_res = cv2.cvtColor(img_res, cv2.COLOR_RGB2BGR)
        res_bytes = cv2.imencode(".png", img_res)[1]
        return res_bytes


class VideoDescriptor(ItemDescriptor):
    """For videos, item_data is the local path of the video file.

    A descriptor made with set_lazy_source() downloads the video the first time item_data is
    read, so videos that no node reads (filtered out, or a pipeline that only changes
    annotations) are never downloaded.
    """

    def __init__(self, info: LegacyProjectItem, item_idx: int, modify_ds_name: bool = True):
        self._lazy_source = None
        self._download_lock = threading.Lock()
        super().__init__(info, item_idx, modify_ds_name)

    @property
    def item_data(self):
        if self._item_data is None and self._lazy_source is not None:
            with self._download_lock:
                if self._item_data is None and self._lazy_source is not None:
                    video_id, video_path = self._lazy_source
                    if not os.path.exists(video_path):
                        import src.globals as g

                        # Another descriptor of the same video may download it at the same
                        # time: write to a private file and rename, so nobody reads a partial one.
                        os.makedirs(os.path.dirname(video_path), exist_ok=True)
                        part_path = f"{video_path}.part-{id(self)}"
                        g.api.video.download_path(video_id, part_path)
                        os.replace(part_path, video_path)
                    self._item_data = video_path
                    self._lazy_source = None
        return self._item_data

    @item_data.setter
    def item_data(self, value):
        self._item_data = value
        self._lazy_source = None

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_download_lock"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._download_lock = threading.Lock()

    def set_lazy_source(self, video_id: int, video_path: str) -> None:
        """Download the video from video_id to video_path when item_data is first read."""
        self._item_data = None
        self._lazy_source = (video_id, video_path)

    def need_write(self) -> bool:
        return self._item_data is not None or self._lazy_source is not None

    def _copy_source_to(self, new_obj: "VideoDescriptor") -> None:
        new_obj._item_data = self._item_data
        new_obj._lazy_source = self._lazy_source

    def clone_with_name(self, new_name):
        new_info = self.info._replace(item_name=new_name)
        new_obj = self.__class__(new_info, self.item_idx)
        self._copy_source_to(new_obj)
        new_obj.res_ds_name = self.res_ds_name
        return new_obj

    def read_video(self) -> cv2.VideoCapture:
        if self.item_data is not None:
            return self.item_data
        video = cv2.VideoCapture(self.get_item_path())
        if not video.isOpened():
            raise RuntimeError("Video not found. {}".format(self.get_item_path()))
        self.item_data = video
        return video

    def write_video_local(self, video_path):
        if self.item_data is None:
            raise RuntimeError("No video data available to write.")

        frame_rate = None
        video_shape = None
        fourcc = cv2.VideoWriter_fourcc(*"MP4V")
        video = cv2.VideoWriter(video_path, fourcc, frame_rate, video_shape)
        for frame in self.item_data:
            video.write(frame)  # Writing the frame
        video.release()

    def encode_video(self):
        if self.item_data is None:
            raise RuntimeError("No video data available to encode.")

        import io

        buffer = io.BytesIO()
        frame_rate = None
        video_shape = None
        fourcc = cv2.VideoWriter_fourcc(*"MP4V")
        video = cv2.VideoWriter(self.item_data, fourcc, frame_rate, video_shape)
        for frame in self.item_data:
            video.write(frame)  # Writing the frame
        video.release()
        buffer.seek(0)
        return buffer.getvalue()
