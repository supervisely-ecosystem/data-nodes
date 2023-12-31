# coding: utf-8

from supervisely import Polygon, Polyline, Label

from src.compute.Layer import Layer
from src.compute.dtl_utils import apply_to_labels
from src.exceptions import WrongGeometryError


# processes FigurePolygon or FigureLine
class ApproxVectorLayer(Layer):
    action = "approx_vector"

    layer_settings = {
        "required": ["settings"],
        "properties": {
            "settings": {
                "type": "object",
                "required": ["classes", "epsilon"],
                "properties": {
                    "classes": {"type": "array", "items": {"type": "string"}},
                    "epsilon": {
                        "type": "number",
                        #     "minimum": 0,
                        #     "exclusiveMinimum": True
                    },
                },
            }
        },
    }

    def __init__(self, config, net):
        Layer.__init__(self, config, net=net)

    def define_classes_mapping(self):
        super().define_classes_mapping()  # don't change

    def modifies_data(self):
        return True

    def process(self, data_el):
        img_desc, ann = data_el
        epsilon = self.settings["epsilon"]

        def approx_contours(label: Label):
            if label.obj_class.name not in self.settings["classes"]:
                return [label]
            if (not isinstance(label.geometry, Polygon)) and (
                not isinstance(label.geometry, Polyline)
            ):
                raise WrongGeometryError(
                    None,
                    "Polyline or Polygon",
                    label.geometry.geometry_name(),
                    extra={"layer": self.action},
                )
            new_geom = label.geometry.approx_dp(epsilon)
            label = label.clone(geometry=new_geom)
            return [label]

        ann = apply_to_labels(ann, approx_contours)
        yield img_desc, ann
