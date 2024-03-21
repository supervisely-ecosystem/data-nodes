# coding: utf-8
from typing import Tuple
from collections import deque

import numpy as np
import networkx as nx

from supervisely import Bitmap, Polyline, Annotation, Label
from supervisely import timeit
from src.compute.dtl_utils.item_descriptor import ImageDescriptor
from src.compute.dtl_utils import apply_to_labels

from src.compute.Layer import Layer
from src.compute.classes_utils import ClassConstants
from src.exceptions import WrongGeometryError


# @TODO: check, it may be dirty


def _get_graph(skel):
    h, w = skel.shape
    G = nx.Graph()
    for i in range(0, h):
        for j in range(0, w):
            if skel[i, j] == 0:
                continue
            G.add_node((i, j))
            if i - 1 >= 0 and j - 1 >= 0 and skel[i - 1, j - 1] == 1:
                G.add_edge((i - 1, j - 1), (i, j))
            if i - 1 >= 0 and skel[i - 1, j] == 1:
                G.add_edge((i - 1, j), (i, j))
            if i - 1 >= 0 and j + 1 < w and skel[i - 1, j + 1] == 1:
                G.add_edge((i - 1, j + 1), (i, j))
            if j - 1 >= 0 and skel[i, j - 1] == 1:
                G.add_edge((i, j - 1), (i, j))

    return G


def _bfs_path(G, v):
    path = list(nx.bfs_edges(G, v))
    try:
        curr = path[-1][1]
    except IndexError:
        raise RuntimeError("Someone hasn't implemented bfs correctly.")
    i = len(path) - 1

    true_path1 = [curr]
    while curr != v:
        if path[i][1] == curr:
            curr = path[i][0]
            true_path1.append(curr)
        i -= 1

    return true_path1[::-1]


def _get_longest_path(G):
    random_node = list(G)[0]
    path1 = _bfs_path(G, random_node)
    last = path1[-1]
    path2 = _bfs_path(G, last)
    longest_path = max([path1, path2], key=len)

    return longest_path


def _get_all_diameters(G: nx.Graph):
    diameters = []

    graphs = list(G.subgraph(c).copy() for c in nx.connected_components(G))
    queue = deque(graphs)
    while queue:
        graph = queue.popleft()
        if graph.number_of_edges() < 3:
            continue
        lpath = _get_longest_path(graph)
        diameters.append(lpath)
        graph.remove_edges_from(list(zip(lpath[:-1], lpath[1:])))
        isolates = list(nx.isolates(graph))
        graph.remove_nodes_from(isolates)
        subgraphs = list(graph.subgraph(c).copy() for c in nx.connected_components(graph))
        queue.extend(subgraphs)

    return diameters


# FigureBitmap to FigureLine
class MaskToLinesLayer(Layer):
    action = "mask_to_lines"
    legacy_action = "bitmap2lines"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["classes_mapping", "min_points_cnt"],
                "properties": {
                    "classes_mapping": {
                        "type": "object",
                        "patternProperties": {".*": {"type": "string"}},
                    },
                    "min_points_cnt": {"type": "integer", "minimum": 2},
                    "approx_epsilon": {"type": "number", "minimum": 0},
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def define_classes_mapping(self):
        for old_class, new_class in self.settings["classes_mapping"].items():
            self.cls_mapping[old_class] = {"title": new_class, "shape": Polyline.geometry_name()}
        self.cls_mapping[ClassConstants.OTHER] = ClassConstants.DEFAULT

    def modifies_data(self):
        return True

    def process(self, data_el: Tuple[ImageDescriptor, Annotation]):
        img_desc, ann = data_el
        approx_epsilon = self.settings.get("approx_epsilon")

        @timeit
        def to_lines(label: Label):
            new_title = self.settings["classes_mapping"].get(label.obj_class.name)
            if new_title is None:
                return [label]
            if not isinstance(label.geometry, Bitmap):
                raise WrongGeometryError(
                    None,
                    "Bitmap",
                    label.geometry.geometry_name(),
                    extra={"layer": self.action},
                )

            origin, mask = label.geometry.origin, label.geometry.data
            graph = _get_graph(mask)
            graph = nx.minimum_spanning_tree(graph)
            paths = _get_all_diameters(graph)

            res = []
            for coords in paths:
                if len(coords) < self.settings["min_points_cnt"]:
                    continue
                coords = np.asarray(coords)
                points = coords + [origin.row, origin.col]

                new_obj_class = label.obj_class.clone(name=new_title, geometry_type=Polyline)
                new_geometry = Polyline(exterior=[(p[0], p[1]) for p in points])

                if approx_epsilon is not None:
                    new_geometry = new_geometry.approx_dp(approx_epsilon)

                res.append(Label(geometry=new_geometry, obj_class=new_obj_class))

            return res

        ann = apply_to_labels(ann, to_lines)
        yield img_desc, ann
