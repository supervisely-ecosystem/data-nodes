from typing import Optional, Union, List
from supervisely.app.widgets import Widget, NotificationBox
from supervisely import ObjClass, ObjClassCollection
from supervisely.app.widgets import Widget, Button, generate_id
from supervisely.app import StateJson

from supervisely.geometry.bitmap import Bitmap
from supervisely.geometry.cuboid import Cuboid
from supervisely.geometry.point import Point
from supervisely.geometry.polygon import Polygon
from supervisely.geometry.polyline import Polyline
from supervisely.geometry.rectangle import Rectangle
from supervisely.geometry.graph import GraphNodes
from supervisely.geometry.any_geometry import AnyGeometry
from supervisely.geometry.cuboid_3d import Cuboid3d
from supervisely.geometry.pointcloud import Pointcloud
from supervisely.geometry.point_3d import Point3d
from supervisely.geometry.multichannel_bitmap import MultichannelBitmap
from supervisely.geometry.closed_surface_mesh import ClosedSurfaceMesh


type_to_shape_text = {
    AnyGeometry: "any shape",
    Rectangle: "rectangle",
    Polygon: "polygon",
    Bitmap: "bitmap (mask)",
    Polyline: "polyline",
    Point: "point",
    Cuboid: "cuboid",  #
    Cuboid3d: "cuboid 3d",
    Pointcloud: "pointcloud",  #  # "zmdi zmdi-border-clear"
    MultichannelBitmap: "n-channel mask",  # "zmdi zmdi-collection-item"
    Point3d: "point 3d",  # "zmdi zmdi-select-all"
    GraphNodes: "keypoints",
    ClosedSurfaceMesh: "volume (3d mask)",
}


class ClassesList(Widget):
    def __init__(
        self,
        classes: Optional[Union[List[ObjClass], ObjClassCollection]] = [],
        multiple: Optional[bool] = False,
        empty_notification: Optional[NotificationBox] = None,
        widget_id: Optional[str] = None,
    ):
        self._classes = classes
        self._multiple = multiple
        if empty_notification is None:
            empty_notification = NotificationBox(
                title="No classes",
                description="Connect node and ensure that source node produces classes of type needed for this node.",
            )
        self.empty_notification = empty_notification
        super().__init__(widget_id=widget_id, file_path=__file__)

        self._select_all_btn = Button(
            "Select all",
            button_type="text",
            show_loading=False,
            icon="zmdi zmdi-check-all",
            widget_id=generate_id(),
        )
        self._deselect_all_btn = Button(
            "Deselect all",
            button_type="text",
            show_loading=False,
            icon="zmdi zmdi-square-o",
            widget_id=generate_id(),
        )

        @self._select_all_btn.click
        def _select_all_btn_clicked():
            self.select_all()
            self.update_state()

        @self._deselect_all_btn.click
        def _deselect_all_btn_clicked():
            self.deselect_all()
            self.update_state()

    def get_json_data(self):
        return {
            "classes": [
                {
                    **cls.to_json(),
                    "shape_text": type_to_shape_text.get(cls.geometry_type).upper(),
                }
                for cls in self._classes
            ]
        }

    def get_json_state(self):
        return {"selected": [False for _ in self._classes]}

    def set(self, classes: Union[List[ObjClass], ObjClassCollection]):
        selected_classes = [cls.name for cls in self.get_selected_classes()]
        self._classes = classes
        StateJson()[self.widget_id]["selected"] = [
            cls.name in selected_classes for cls in self._classes
        ]
        self.update_data()
        StateJson().send_changes()

    def get_selected_classes(self):
        selected = StateJson()[self.widget_id]["selected"]
        return [cls for cls, is_selected in zip(self._classes, selected) if is_selected]

    def select_all(self):
        StateJson()[self.widget_id]["selected"] = [True for _ in self._classes]
        StateJson().send_changes()

    def deselect_all(self):
        StateJson()[self.widget_id]["selected"] = [False for _ in self._classes]
        StateJson().send_changes()

    def select(self, names: List[str]):
        selected = [cls.name in names for cls in self._classes]
        StateJson()[self.widget_id]["selected"] = selected
        StateJson().send_changes()

    def get_all_classes(self):
        return self._classes
