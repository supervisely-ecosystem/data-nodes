from typing import List, Dict
from supervisely.app.widgets import Widget
from supervisely.app import StateJson, DataJson


class AugsList(Widget):
    class Routes:
        MOVE_AUG_UP = "move_aug_up_cb"
        MOVE_AUG_DOWN = "move_aug_down_cb"
        DELETE_AUG = "delete_aug_cb"

    class AugItem:
        def __init__(
            self,
            category: str,
            name: str,
            params: dict,
            sometimes: float = None,
            python: str = None,
        ) -> None:
            self.category = category
            self.name = name
            self.params = params
            self.sometimes = sometimes

            if python is None:
                self.python = self._generate_py()
            else:
                self.python = python

        def _generate_py(self):
            py = f"iaa.{self.name}({', '.join([f'{k}={repr(v)}' if isinstance(v, str) else f'{k}={v}' for k, v in self.params.items()])})"
            if self.sometimes is not None:
                py = f"iaa.Sometimes({self.sometimes}, {py})"
            return py

        def get_py(self):
            return self.python

        def to_json(self):
            return {
                "category": self.category,
                "name": self.name,
                "params": self.params,
                "sometimes": self.sometimes,
                "python": self.python,
            }

    def __init__(self, pipeline: List[AugItem] = [], shuffle: bool = False, widget_id: str = None):
        self._pipeline = pipeline
        self._shuffle = shuffle
        self._py_options = {
            "mode": "ace/mode/python",
            "showGutter": False,
            "readOnly": True,
            "maxLines": 1,
            "highlightActiveLine": False,
        }

        self._delete_aug_clicked = False
        self._move_aug_up_clicked = False
        self._move_aug_down_clicked = False
        self._pipeline_json = [aug.get_py() for aug in self._pipeline]
        super().__init__(widget_id=widget_id, file_path=__file__)

        server = self._sly_app.get_server()

        # DELETE_AUG
        del_route_path = self.get_route_path(AugsList.Routes.DELETE_AUG)

        @server.post(del_route_path)
        def _click():
            index = StateJson()[self.widget_id]["augIndex"]
            if index is not None:
                del self._pipeline[index]
            self._pipeline_json = [aug.get_py() for aug in self._pipeline]
            DataJson()[self.widget_id]["pipeline"] = self._pipeline_json
            DataJson().send_changes()
            StateJson()[self.widget_id]["augIndex"] = None
            StateJson().send_changes()

        # MOVE_AUG_UP
        mv_up_route_path = self.get_route_path(AugsList.Routes.MOVE_AUG_UP)

        @server.post(mv_up_route_path)
        def _click():
            index = StateJson()[self.widget_id]["augIndex"]
            if index is not None and index > 0:
                a = self._pipeline[index - 1]
                self._pipeline[index - 1] = self._pipeline[index]
                self._pipeline[index] = a
            self._pipeline_json = [aug.get_py() for aug in self._pipeline]
            DataJson()[self.widget_id]["pipeline"] = self._pipeline_json
            DataJson().send_changes()
            StateJson()[self.widget_id]["augIndex"] = None
            StateJson().send_changes()
            return

        # MOVE_AUG_DOWN
        mv_down_route_path = self.get_route_path(AugsList.Routes.MOVE_AUG_DOWN)

        @server.post(mv_down_route_path)
        def _click():
            index = StateJson()[self.widget_id]["augIndex"]
            if index is not None and index < len(self._pipeline) - 1:
                a = self._pipeline[index + 1]
                self._pipeline[index + 1] = self._pipeline[index]
                self._pipeline[index] = a
            self._pipeline_json = [aug.get_py() for aug in self._pipeline]
            DataJson()[self.widget_id]["pipeline"] = self._pipeline_json
            DataJson().send_changes()
            StateJson()[self.widget_id]["augIndex"] = None
            StateJson().send_changes()
            return

    def get_json_data(self):
        return {
            "pipeline": self._pipeline_json,
        }

    def get_json_state(self):
        return {
            "shuffle": self._shuffle,
            "options": self._py_options,
            "augIndex": None,
        }

    def get_pipeline(self):
        return [aug.to_json() for aug in self._pipeline]

    def get_pipeline_raw(self):
        return self._pipeline

    def set_pipeline(self, pipeline):
        self._pipeline = pipeline
        self._pipeline_json = [aug.get_py() for aug in self._pipeline]
        DataJson()[self.widget_id]["pipeline"] = self._pipeline_json
        DataJson().send_changes()

    def append_aug(
        self, category: str, name: str, params: dict, sometimes: float = None, python: str = None
    ):
        aug = AugsList.AugItem(category, name, params, sometimes, python)
        self._pipeline.append(aug)
        self._pipeline_json = [aug.get_py() for aug in self._pipeline]
        DataJson()[self.widget_id]["pipeline"] = self._pipeline_json
        DataJson().send_changes()

    def is_shuffled(self) -> bool:
        return StateJson()[self.widget_id]["shuffle"]

    def set_shuffle(self, shuffle: bool):
        self._shuffle = shuffle
        StateJson()[self.widget_id]["shuffle"] = shuffle
        StateJson().send_changes()

    def from_json(self, data: List[Dict], shuffle: bool = False):
        pipeline = [AugsList.AugItem(**aug) for aug in data]
        self.set_pipeline(pipeline)
        self.set_shuffle(shuffle)
