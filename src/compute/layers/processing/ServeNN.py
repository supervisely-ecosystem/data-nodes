# coding: utf-8
from supervisely import logger as sly_logger
from typing import Tuple
import numpy as np
from os.path import join

from src.compute.Layer import Layer
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from supervisely.nn.inference import Session
from src.compute.classes_utils import ClassConstants
from src.compute.tags_utils import TagConstants
from supervisely.collection.key_indexed_collection import KeyIndexedCollection
from supervisely import ProjectMeta, Annotation, ObjClass, TagMeta, TagCollection
import supervisely.imaging.image as sly_image
from supervisely.io.fs import silent_remove, file_exists
import src.globals as g


class ServeNN(Layer):
    action = "serve_nn"

    layer_settings = {}

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def requires_item(self):
        return False

    def modifies_data(self):
        return False

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el
        img = img_desc.read_image()
        img = img.astype(np.uint8)

        yield img_desc, ann

    # def validate(self):
    #     super().validate()
    #     if self.settings["session_id"] is None:
    #         raise ValueError("Serve NN layer requires model to be connected")
