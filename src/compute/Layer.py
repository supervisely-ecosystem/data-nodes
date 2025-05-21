# coding: utf-8

from __future__ import division
from os.path import join
import shutil
from copy import deepcopy
from typing import Tuple, List
from time import time

import jsonschema

from supervisely import ProjectMeta, TagMeta, ObjClass, Annotation, rand_str
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from src.compute.utils import json_utils
from src.compute.utils import os_utils
from src.compute.utils.stat_timer import TinyTimer, global_timer
from supervisely.sly_logger import logger
from supervisely.annotation.json_geometries_map import GET_GEOMETRY_FROM_STR
from supervisely.imaging.color import hex2rgb

from src.compute.classes_utils import ClassConstants
from src.compute.tags_utils import TagConstants
from src.exceptions import CustomException, GraphError, CreateMetaError


def maybe_wrap_in_list(v):
    return v if isinstance(v, list) else [v]


def check_connection_name(connection_name):
    if len(connection_name) == 0:
        raise GraphError("Connection name should be non empty.")
    if isinstance(connection_name, dict):
        for k in connection_name:
            if connection_name[k][0][0] != "$":
                raise GraphError(f'Connection name should be "{Layer.null}" or start with "$".')
    else:
        if connection_name[0] != "$" and connection_name != Layer.null:
            raise GraphError(f'Connection name should be "{Layer.null}" or start with "$".')


class Layer:
    null = "null"
    # action = "layer"

    base_params = {
        "definitions": {
            "connections": {
                "oneOf": [
                    {"type": "object"},
                    {"type": "array", "items": {"type": "string"}, "minItems": 0},
                ]
            },
            "color": {
                "type": "array",
                "items": {"type": "integer", "minimum": 0, "maximum": 255},
                "maxItems": 3,
                "minItems": 3,
            },
            "probability": {"type": "number", "minimum": 0, "maximum": 1},
            "percent": {"type": "number", "minimum": 0, "maximum": 100},
        },
        "type": "object",
        "required": ["action", "src", "dst"],
        "properties": {
            "action": {"type": "string"},
            "src": {"$ref": "#/definitions/connections"},
            "dst": {
                "oneOf": [
                    {"type": "array"},
                    {"type": "string"},
                ]
            },
        },
    }

    layer_settings_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "required": {"type": "array", "items": {"type": "string", "enum": ["settings"]}},
            "properties": {
                "type": "object",
                "properties": {"settings": {}, "src": {}, "dst": {}},
                "required": ["settings"],
                "additionalProperties": False,
            },
        },
    }

    actions_mapping = {}

    def __init__(self, config, net=None):
        self._config = deepcopy(config)
        self.net = net

        self.srcs = maybe_wrap_in_list(config["src"])
        self.dsts = maybe_wrap_in_list(config["dst"])

        self.settings = config.get("settings", {})
        self.postprocess_cb = config.get("postprocess_cb", None)

        self.cls_mapping = {}
        self.tag_mapping = {}
        self.define_classes_mapping()
        self.define_tags_mapping()
        self.output_meta = None

        # for save layers
        self.existing_names = {}

    @classmethod
    def get_action(cls):
        return cls.action

    def validate(self):
        try:
            jsonschema.validate(self._config, self.params)
        except jsonschema.ValidationError as e:
            extra = {"layer_config": self._config, "error": e.message}

            # v = jsonschema.Draft202012Validator(self.params)
            # for error in v.iter_errors(self._config):
            #     extra.setdefault("errors", []).append(str(error))
            raise GraphError(f"Layer not valid. Error: {e}", error=e, extra=extra)
        try:
            self.validate_source_connections()
            self.validate_dest_connections()
        except GraphError as e:
            e.extra["layer_config"] = self._config
            raise e

    @property
    def config(self):
        return deepcopy(self._config)

    def define_classes_mapping(self):
        self.cls_mapping[ClassConstants.OTHER] = ClassConstants.DEFAULT

    def define_tags_mapping(self):
        self.tag_mapping[TagConstants.OTHER] = TagConstants.DEFAULT

    def get_added_tag_metas(self):
        return []

    def get_removed_tag_metas(self):
        return []

    def requires_item(self):
        """Defines if Layer require that data have to be downloaded"""
        return False

    def modifies_data(self):
        """Defines if data or it's annotation is modified by the Layer"""
        return False

    def validate_source_connections(self):
        for src in self.srcs:
            if src == Layer.null:
                raise GraphError(f'"Layer.null" cannot be in "src"')
            check_connection_name(src)

    def validate_dest_connections(self):
        for dst in self.dsts:
            check_connection_name(dst)

    # input_metas_dict: src datalevel name -> meta for the datalevel
    def make_output_meta(self, input_metas_dict):
        try:
            # if len(self.cls_mapping) == 0:
            #     raise RuntimeError("Empty cls_mapping for layer: {}".format(self.action))

            full_input_meta = ProjectMeta()
            for inp_meta in input_metas_dict.values():
                for inp_obj_class in inp_meta.obj_classes:
                    existing_obj_class = full_input_meta.obj_classes.get(inp_obj_class.name, None)
                    if existing_obj_class is None:
                        full_input_meta = full_input_meta.add_obj_class(inp_obj_class)
                    elif existing_obj_class.geometry_type != inp_obj_class.geometry_type:
                        raise CreateMetaError(
                            "Trying to add existing ObjClass with different geometry type",
                            extra={
                                "existing_class": existing_obj_class.to_json(),
                                "new_class": inp_obj_class.to_json(),
                            },
                        )
                        # raise RuntimeError(
                        #     f"Trying to add new class ({inp_obj_class.name}) with shape ({inp_obj_class.geometry_type.geometry_name()}). Same class with different shape ({existing_obj_class.geometry_type.geometry_name()}) exists."
                        # )
                for inp_tag_meta in inp_meta.tag_metas:
                    existing_tag_meta = full_input_meta.tag_metas.get(inp_tag_meta.name, None)
                    if existing_tag_meta is None:
                        full_input_meta = full_input_meta.add_tag_meta(inp_tag_meta)
                    elif not existing_tag_meta.is_compatible(inp_tag_meta):
                        raise CreateMetaError(
                            "Trying to add existing TagMeta with different type or possible values",
                            extra={
                                "existing_tag_meta": existing_tag_meta.to_json(),
                                "new_tag_meta": inp_tag_meta.to_json(),
                            },
                        )
                        # raise RuntimeError(
                        #     f"Trying to add new tag ({inp_tag_meta.name}) with type ({inp_tag_meta.value_type}) and possible values ({inp_tag_meta.possible_values}). Same tag with different type ({existing_tag_meta.value_type}) or possible values ({existing_tag_meta.possible_values}) exists."
                        # )

            res_meta = deepcopy(full_input_meta)
            in_class_titles = set((obj_class.name for obj_class in full_input_meta.obj_classes))

            ### CLASSES
            # __other__ -> smth
            if ClassConstants.OTHER in self.cls_mapping:
                other_classes = in_class_titles - set(self.cls_mapping.keys())
                for oclass in other_classes:
                    self.cls_mapping[oclass] = self.cls_mapping[ClassConstants.OTHER]
                del self.cls_mapping[ClassConstants.OTHER]

            missing_classes = in_class_titles - set(self.cls_mapping.keys())
            if len(missing_classes) != 0:
                raise CreateMetaError(
                    "Some classes in input meta are missing in mapping",
                    extra={
                        "missing_classes": [
                            res_meta.obj_classes.get(obj_class_name)
                            for obj_class_name in missing_classes
                        ]
                    },
                )

            for src_class_title, dst_class in self.cls_mapping.items():
                # __new__ -> [ list of classes ]
                if src_class_title == ClassConstants.NEW:
                    if type(dst_class) is not list:
                        raise RuntimeError("Internal class mapping error in layer (NEW spec).")
                    for new_cls_dict in dst_class:
                        new_name = new_cls_dict["title"]
                        new_shape = new_cls_dict["shape"]
                        new_geometry_type = GET_GEOMETRY_FROM_STR(new_shape)
                        new_geometry_config = new_cls_dict.get("geometry_config")
                        new_color = new_cls_dict.get("color", None)
                        if new_color is not None and new_color[0] == "#":
                            new_color = hex2rgb(new_color)
                        inp_obj_class = ObjClass(
                            new_name, new_geometry_type, new_color, new_geometry_config
                        )
                        if res_meta.obj_classes.has_key(new_name):
                            existing_obj_class = res_meta.obj_classes.get(new_name)
                            if existing_obj_class.geometry_type != new_geometry_type:
                                raise CreateMetaError(
                                    "Trying to add existing ObjClass with different geometry type",
                                    extra={
                                        "existing_class": existing_obj_class.to_json(),
                                        "new_class": inp_obj_class.to_json(),
                                    },
                                )
                        else:
                            res_meta = res_meta.add_obj_class(inp_obj_class)

                # __clone__ -> dict {parent_cls_name: child_cls_name}
                elif src_class_title == ClassConstants.CLONE:
                    if type(dst_class) is not dict:
                        raise RuntimeError("Internal class mapping error in layer (CLONE spec).")

                    for src_title, dst_title in dst_class.items():
                        if src_title == "__other__":
                            continue
                        real_src_cls = res_meta.obj_classes.get(src_title, None)
                        if real_src_cls is None:
                            raise CreateMetaError(
                                "Class not found in input meta",
                                extra={
                                    "class_name": src_title,
                                    "existing_classes": res_meta.obj_classes.to_json(),
                                },
                            )
                        if real_src_cls.name == dst_title:
                            continue
                        real_dst_cls = real_src_cls.clone(name=dst_title)
                        res_meta = res_meta.add_obj_class(real_dst_cls)

                elif src_class_title == ClassConstants.UPDATE:
                    if type(dst_class) is not list:
                        raise RuntimeError("Internal class mapping error in layer (NEW spec).")

                    for cls_dct in dst_class:
                        title = cls_dct["title"]
                        existing_class = res_meta.obj_classes.get(title, None)
                        if existing_class is None:
                            raise CreateMetaError(
                                "Class not found in input meta",
                                extra={
                                    "class_name": title,
                                    "existing_classes": res_meta.obj_classes.to_json(),
                                },
                            )
                        new_shape = cls_dct.get("shape", None)
                        new_geometry_type = GET_GEOMETRY_FROM_STR(new_shape) if new_shape else None
                        new_color = cls_dct.get("color", None)
                        if new_color is not None and new_color[0] == "#":
                            new_color = hex2rgb(new_color)
                        new_obj_cls = existing_class.clone(
                            name=title, geometry_type=new_geometry_type, color=new_color
                        )
                        res_meta = res_meta.delete_obj_class(title)
                        res_meta = res_meta.add_obj_class(new_obj_cls)

                # smth -> __default__
                elif dst_class == ClassConstants.DEFAULT:
                    pass

                # smth -> __clone__
                elif dst_class == ClassConstants.CLONE:
                    pass

                # smth -> __ignore__
                elif dst_class == ClassConstants.IGNORE:
                    res_meta = res_meta.delete_obj_class(src_class_title)

                # smth -> merge
                elif type(dst_class) is str and dst_class.startswith(ClassConstants.MERGE):
                    obj_cls = res_meta.get_obj_class(src_class_title)
                    if obj_cls is None:
                        logger.debug(
                            "Class not found in input meta",
                            extra={"class_name": src_class_title, "dst_class": dst_class},
                        )
                    else:
                        res_meta = res_meta.delete_obj_class(src_class_title)

                # smth -> new name
                elif type(dst_class) is str:
                    obj_cls = res_meta.get_obj_class(src_class_title)
                    if obj_cls is None:
                        logger.debug(
                            "Class not found in input meta",
                            extra={"class_name": src_class_title, "dst_class": dst_class},
                        )
                    else:
                        obj_cls = obj_cls.clone(name=dst_class)
                        res_meta = res_meta.delete_obj_class(src_class_title)
                        res_meta = res_meta.add_obj_class(obj_cls)

                # smth -> new cls description
                elif type(dst_class) is dict:
                    new_name = dst_class.get("title", None)
                    new_shape = dst_class.get("shape", None)
                    new_geometry_type = GET_GEOMETRY_FROM_STR(new_shape) if new_shape else None
                    new_color = dst_class.get("color", None)
                    if new_color is not None and new_color[0] == "#":
                        new_color = hex2rgb(new_color)
                    obj_cls = res_meta.get_obj_class(src_class_title)
                    if obj_cls is None:
                        obj_cls = ObjClass(new_name, new_geometry_type, new_color)
                    else:
                        obj_cls = obj_cls.clone(
                            name=new_name, geometry_type=new_geometry_type, color=new_color
                        )
                    res_meta = res_meta.delete_obj_class(src_class_title)
                    res_meta = res_meta.add_obj_class(obj_cls)
            ### ------------------

            ### TAGS
            in_tags_titles = set((tag_meta.name for tag_meta in full_input_meta.tag_metas))

            if TagConstants.OTHER in self.tag_mapping:
                other_tags = in_tags_titles - set(self.tag_mapping.keys())
                for otag in other_tags:
                    self.tag_mapping[otag] = self.tag_mapping[TagConstants.OTHER]
                del self.tag_mapping[TagConstants.OTHER]

            missing_tags = in_tags_titles - set(self.tag_mapping.keys())
            if len(missing_tags) != 0:
                raise CreateMetaError(
                    "Some tags in input meta are missing in mapping",
                    extra={
                        "missing_tags": [
                            res_meta.tag_metas.get(tag_meta_name) for tag_meta_name in missing_tags
                        ]
                    },
                )

            for src_tag_title, dst_tag in self.tag_mapping.items():
                # __new__ -> [ list of tags ]
                if src_tag_title == TagConstants.NEW:
                    if type(dst_tag) is not list:
                        raise RuntimeError("Internal tag meta mapping error in layer (NEW spec).")
                    for new_tag_dict in dst_tag:
                        new_name = new_tag_dict["title"]
                        new_value_type = new_tag_dict["value_type"]
                        new_color = new_tag_dict.get("color", None)
                        if new_color is not None and new_color[0] == "#":
                            new_color = hex2rgb(new_color)
                        new_possible_values = new_tag_dict.get("possible_values", None)
                        new_applicable_to = new_tag_dict.get("applicable_to", None)
                        new_applicable_classes = new_tag_dict.get("applicable_classes", None)
                        inp_tag_meta = TagMeta(
                            name=new_name,
                            value_type=new_value_type,
                            possible_values=new_possible_values,
                            color=new_color,
                            applicable_to=new_applicable_to,
                            applicable_classes=new_applicable_classes,
                        )
                        if res_meta.tag_metas.has_key(new_name):
                            existing_tag_meta = res_meta.tag_metas.get(new_name)
                            if existing_tag_meta.value_type != new_value_type:
                                raise CreateMetaError(
                                    "Trying to add existing TagMeta with different value type",
                                    extra={
                                        "existing_tag_meta": existing_tag_meta.to_json(),
                                        "new_tag_meta": inp_tag_meta.to_json(),
                                    },
                                )
                        else:
                            res_meta = res_meta.add_tag_meta(inp_tag_meta)

                # __clone__ -> dict {parent_tag_name: child_tag_name}
                elif src_tag_title == TagConstants.CLONE:
                    if type(dst_tag) is not dict:
                        raise RuntimeError("Internal tag mapping error in layer (CLONE spec).")

                    for src_title, dst_title in dst_tag.items():
                        if src_title == "__other__":
                            continue
                        real_src_tag = res_meta.tag_metas.get(src_title, None)
                        if real_src_tag is None:
                            raise CreateMetaError(
                                "TagMeta not found in input meta",
                                extra={
                                    "tag_meta_name": src_title,
                                    "existing_tag_metas": res_meta.tag_metas.to_json(),
                                },
                            )
                        if real_src_tag.name == dst_title:
                            continue
                        real_dst_tag = real_src_tag.clone(name=dst_title)
                        res_meta = res_meta.add_tag_meta(real_dst_tag)

                # __update__ -> [ list of tags ]
                elif src_tag_title == TagConstants.UPDATE:
                    if type(dst_tag) is not list:
                        raise RuntimeError("Internal tag mapping error in layer (NEW spec).")

                    for tag_dct in dst_tag:
                        title = tag_dct["title"]
                        existing_tag = res_meta.tag_metas.get(title, None)
                        if existing_tag is None:
                            raise CreateMetaError(
                                "TagMeta not found in input meta",
                                extra={
                                    "tag_meta_name": title,
                                    "existing_tag_metas": res_meta.tag_metas.to_json(),
                                },
                            )
                        new_value_type = tag_dct.get("value_type", None)
                        new_color = tag_dct.get("color", None)
                        if new_color is not None and new_color[0] == "#":
                            new_color = hex2rgb(new_color)
                        new_possible_values = new_tag_dict.get("possible_values", None)
                        new_applicable_to = new_tag_dict.get("applicable_to", None)
                        new_applicable_classes = new_tag_dict.get("applicable_classes", None)

                        new_tag_meta = existing_tag.clone(
                            name=title,
                            value_type=new_value_type,
                            possible_values=new_possible_values,
                            color=new_color,
                            applicable_to=new_applicable_to,
                            applicable_classes=new_applicable_classes,
                        )
                        res_meta = res_meta.delete_tag_meta(title)
                        res_meta = res_meta.add_tag_meta(new_tag_meta)

                # smth -> __default__
                elif dst_tag == TagConstants.DEFAULT:
                    pass

                # smth -> __clone__
                elif dst_tag == TagConstants.CLONE:
                    pass

                # smth -> __ignore__
                elif dst_tag == TagConstants.IGNORE:
                    res_meta = res_meta.delete_tag_meta(src_tag_title)

                # smth -> new name
                elif type(dst_tag) is str:
                    tag_meta = res_meta.get_tag_meta(src_tag_title)
                    tag_meta = tag_meta.clone(name=dst_tag)
                    res_meta = res_meta.delete_tag_meta(src_tag_title)
                    res_meta = res_meta.add_tag_meta(tag_meta)

                # smth -> new tag description
                elif type(dst_tag) is dict:
                    new_name = dst_tag.get("title", None)
                    new_value_type = dst_tag.get("value_type", None)
                    new_color = dst_tag.get("color", None)
                    if new_color is not None and new_color[0] == "#":
                        new_color = hex2rgb(new_color)
                    new_possible_values = dst_tag.get("possible_values", None)
                    new_applicable_to = dst_tag.get("applicable_to", None)
                    new_applicable_classes = dst_tag.get("applicable_classes", None)
                    inp_tag_meta = TagMeta(
                        name=new_name,
                        value_type=new_value_type,
                        possible_values=new_possible_values,
                        color=new_color,
                        applicable_to=new_applicable_to,
                        applicable_classes=new_applicable_classes,
                    )

                    tag_meta = res_meta.get_tag_meta(src_tag_title)
                    if tag_meta is None:
                        tag_meta = TagMeta(
                            name=new_name, value_type=new_value_type, color=new_color
                        )
                    else:
                        tag_meta = tag_meta.clone(
                            name=new_name,
                            value_type=new_value_type,
                            possible_values=new_possible_values,
                            color=new_color,
                            new_applicable_to=new_applicable_to,
                            applicable_classes=new_applicable_classes,
                        )
                    res_meta = res_meta.delete_tag_meta(src_tag_title)
                    res_meta = res_meta.add_tag_meta(tag_meta)
            ### ------------------

            self.output_meta = res_meta
        except CustomException as e:
            e.extra["layer_config"] = self._config
            raise e
        except:
            raise

        return self.output_meta

    # def verbose_pre_start(self, total):
    #     shared_utils.e(self, '%d elements to process.' % total, 'INFO')
    #     self.total_samples = total
    #
    # verbose_interval = 100
    #
    # def get_total(self):
    #     if hasattr(self, 'total_samples'):
    #         return self.total_samples
    #     else:
    #         return -1
    #
    # def verbose_process(self, cur, name='', dataset_name=''):
    #     total = self.get_total()
    #     if shared_utils.IS_PROD() and total != -1 and hasattr(self, 'step') and hasattr(self, 'steps'):
    #         msg = 'Processed sample "%s" from dataset "%s"' % (name, dataset_name)
    #         logger.info(msg, extra={'progress': {
    #             'name': 'DATA_LAYER',
    #             'step': self.step,
    #             'steps': self.steps,
    #             'current': cur,
    #             'total': total,
    #         }})
    #     else:
    #         if cur % Layer.verbose_interval == 0:
    #             shared_utils.e(self,
    #                     'Processed %d%s elements.' % (cur,
    #                                                  '' if total == -1 else
    #                                                  '/%d (%.2f%%)' % (total, 100 * cur / total)),
    #                     'INFO')
    #
    # def verbose_post_start(self, cur):
    #     total = self.get_total()
    #     shared_utils.e(self,
    #             'Done processing %d%s elements.' % (cur,
    #                                                '' if total == -1 else
    #                                                '/%d (%.2f%%)' % (total, 100 * cur / total)),
    #             'INFO')

    def description(self):
        return 'action: "%s", src: %s, dst: %s' % (
            self.__class__.action,
            "[%s]" % ", ".join(map(lambda x: '"%s"' % x, self.srcs)),
            "[%s]" % ", ".join(map(lambda x: '"%s"' % x, self.dsts)),
        )

    def preprocess(self):
        pass

    # def process_timer(func):
    #     def wrapper(self, *args, **kwargs):
    #         if self.net.preview_mode:
    #             result = func(self, *args, **kwargs)
    #         else:
    #             start_time = time()
    #             result = func(self, *args, **kwargs)
    #             end_time = time()
    #             logger.debug(
    #                 f"{self.action} '{func.__name__}' time: {end_time - start_time:.10f} seconds."
    #             )
    #         return result
    #     return wrapper

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        raise NotImplementedError()

    def process_batch(self, data_els: List[Tuple[ImageDescriptor, Annotation]]):
        raise NotImplementedError()

    def has_batch_processing(self) -> bool:
        return False

    def postprocess(self):
        pass

    def process_timed(self, data_batch: List[Tuple[ImageDescriptor, Annotation]]):
        tm = TinyTimer()
        if self.has_batch_processing():
            for layer_outputs in self.process_batch(data_batch):
                global_timer.add_value(
                    {
                        "action_name": self.__class__.action,
                        "id": id(self),
                        "items_count": len(data_batch),
                    },
                    tm.get_sec(),
                )
                tm = TinyTimer()
                yield layer_outputs
        else:
            layer_outputs = []
            # logger.debug(
            #     f"'{self.__class__.action}' doesn't have batch processing. Items will be processed 1 by 1."
            # )
            for data_el, ann in data_batch:
                for layer_output in self.process((data_el, ann)):
                    layer_outputs.append(layer_output)
            global_timer.add_value(
                {
                    "action_name": self.__class__.action,
                    "id": id(self),
                    "items_count": len(data_batch),
                },
                tm.get_sec(),
            )
            tm = TinyTimer()
            yield layer_outputs

    @staticmethod
    def get_params(cls):
        if cls == Layer:
            raise RuntimeError("Class Layer has no params.")
        else:
            if not hasattr(cls, "layer_settings"):
                raise RuntimeError('Layer "%s" has no attribute "layer_settings"' % cls.__name__)

        layer_params = deepcopy(Layer.base_params)

        layer_params["properties"]["action"]["enum"] = [cls.action]

        layer_params["required"] += cls.layer_settings.get("required", [])
        layer_params["properties"].update(cls.layer_settings.get("properties", dict()))

        # print cls.action, layer_params['properties']

        layer_params = add_false_additional_properties(layer_params)

        return layer_params

    @staticmethod
    def dump_schemas(output_path):
        output_path = join(output_path, "schemas")
        shutil.rmtree(output_path)
        layers_output_path = join(output_path, "layers")
        os_utils.mkdir(layers_output_path)
        global_schema = {"definitions": deepcopy(Layer.base_params["definitions"])}
        global_schema["definitions"]["layers"] = dict()
        global_schema["items"] = {"anyOf": []}
        # global_schema['items']['minItems'] = 1
        # global_schema['items']['maxItems'] = 1

        for action, cls in Layer.actions_mapping.items():
            layer_schema = deepcopy(cls.params)
            json_utils.json_dump(
                layer_schema, join(layers_output_path, "%s.json" % (action)), indent=4
            )
            del layer_schema["definitions"]
            global_schema["definitions"]["layers"][action] = layer_schema
            global_schema["items"]["anyOf"].append({"$ref": "#/definitions/layers/%s" % action})

        json_utils.json_dump(global_schema, join(output_path, "schema.json"), indent=4)

    @staticmethod
    def register_layer(cls, type):
        if not hasattr(cls, "action"):
            raise RuntimeError('Layer "%s" has no attribute "action"' % cls.__name__)
        action = cls.get_action()
        if action in Layer.actions_mapping:
            raise RuntimeError('Duplicate action "%s"' % action)

        jsonschema.validate(cls.layer_settings, Layer.layer_settings_schema)
        Layer.actions_mapping[action] = cls
        cls.params = Layer.get_params(cls)
        cls.type = type

    # def get_folder_from_ann(self, ann, tag2folder):
    #     img_info = shared_utils.get_img_info(ann)
    #     if len(ann.tags) == 0:
    #         raise RuntimeError('No tags found for %s.' % img_info)
    #     if ann.tags[-1] not in tag2folder:
    #         raise RuntimeError('No mapping for tag "%s" for %s.' % (ann.tags[-1], img_info))
    #     folder = tag2folder[ann.tags[-1]]
    #     return folder

    def get_free_name(self, name: str, dataset_name: str, project_name: str):
        new_name = name
        full_ds_name = f"{project_name}/{dataset_name}"
        names_in_ds = self.existing_names.get(full_ds_name, set())

        while new_name in names_in_ds:
            new_name = name + "_" + rand_str(10)

        names_in_ds.add(new_name)
        self.existing_names[full_ds_name] = names_in_ds

        return new_name


def add_false_additional_properties(params):
    if type(params) == dict:
        for el in params:
            params[el] = add_false_additional_properties(params[el])
    if type(params) == list:
        for i in range(len(params)):
            params[i] = add_false_additional_properties(params[i])
    if type(params) == dict:
        if "required" in params:
            params["additionalProperties"] = False
    return params
