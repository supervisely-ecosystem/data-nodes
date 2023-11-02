from typing import Optional, Union, List

from supervisely import TagMeta, TagMetaCollection
from supervisely.app import StateJson
from supervisely.app.widgets import Widget, ObjectClassView


class TagMetasListPreview(Widget):
    def __init__(
        self,
        tag_metas: Optional[Union[List[TagMeta], TagMetaCollection]] = [],
        max_height: str = "128px",
        widget_id: Optional[str] = None,
    ):
        self._tag_metas = tag_metas
        self._max_height = max_height
        super().__init__(widget_id=widget_id, file_path=__file__)

    def get_json_data(self):
        return {
            "max_height": self._max_height,
        }

    def get_json_state(self):
        return {"tag_metas": [cls for cls in self._tag_metas]}

    def set(self, tag_metas: Union[List[TagMeta], TagMetaCollection]):
        self._tag_metas = [TagMetaView(cls, True, True).get_json_data() for cls in tag_metas]
        StateJson()[self.widget_id] = self.get_json_state()
        StateJson().send_changes()

    def get(self):
        return self._tag_metas
