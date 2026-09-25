# coding: utf-8

from typing import Dict, Optional

from supervisely import AnyGeometry, GraphNodes, ObjClass
from supervisely.geometry.graph import NODES

from src.exceptions import BadSettingsError


class ClassConstants:
    OTHER = "__other__"
    IGNORE = "__ignore__"
    DEFAULT = "__default__"
    UPDATE = "__update__"
    NEW = "__new__"
    CLONE = "__clone__"
    MERGE = "__merge__"
    SHAPES = ['bitmap', 'polygon', 'rectangle', 'line', 'point']


def get_merge_nodes_mapping(src_class: ObjClass, dst_class: ObjClass) -> Optional[Dict[str, str]]:
    """Check that src_class can be merged into dst_class.

    Returns a mapping of source template node keys to target template node keys
    for keypoint (graph) classes, and None for other shapes.
    Nodes are matched by their label, so templates with different keys can be merged.
    """
    extra = {
        "class": src_class.name,
        "target_class": dst_class.name,
        "shape": src_class.geometry_type.geometry_name(),
        "target_shape": dst_class.geometry_type.geometry_name(),
    }
    if dst_class.geometry_type is AnyGeometry and src_class.geometry_type is not GraphNodes:
        return None
    if src_class.geometry_type != dst_class.geometry_type:
        raise BadSettingsError("Can not merge classes with different shapes", extra=extra)
    if src_class.geometry_type is not GraphNodes:
        return None

    src_nodes = src_class.geometry_config[NODES]
    dst_nodes = dst_class.geometry_config[NODES]
    dst_keys_by_label = {}
    for dst_key, dst_node in dst_nodes.items():
        dst_keys_by_label.setdefault(dst_node.get("label"), []).append(dst_key)

    mapping = {}
    for src_key, src_node in src_nodes.items():
        node_label = src_node.get("label")
        if src_key in dst_nodes and dst_nodes[src_key].get("label") == node_label:
            mapping[src_key] = src_key
            continue
        dst_keys = dst_keys_by_label.get(node_label, [])
        if len(dst_keys) == 0:
            raise BadSettingsError(
                "Keypoint of the source class is missing in the target class template",
                extra={**extra, "keypoint": node_label},
            )
        if len(dst_keys) > 1:
            raise BadSettingsError(
                "Keypoint label is not unique in the target class template",
                extra={**extra, "keypoint": node_label},
            )
        mapping[src_key] = dst_keys[0]

    if len(set(mapping.values())) != len(mapping):
        raise BadSettingsError(
            "Keypoint labels are not unique in the source class template", extra=extra
        )
    return mapping


def remap_graph_nodes(geometry: GraphNodes, nodes_mapping: Dict[str, str]) -> GraphNodes:
    """Rebuild a graph geometry with node keys of the target class template."""
    nodes = {nodes_mapping[key]: node for key, node in geometry.nodes.items()}
    return GraphNodes(
        nodes,
        sly_id=geometry.sly_id,
        class_id=geometry.class_id,
        labeler_login=geometry.labeler_login,
        updated_at=geometry.updated_at,
        created_at=geometry.created_at,
    )
