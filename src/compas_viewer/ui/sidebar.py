from typing import TYPE_CHECKING
from typing import Callable

from PySide6 import QtCore
from PySide6.QtWidgets import QSplitter

from compas_viewer.components import Sceneform
from compas_viewer.components.objectsetting import ObjectSetting
from compas_viewer.ui.container import Container

if TYPE_CHECKING:
    from .ui import UI


class SideBarRight(Container):
    def __init__(self, ui: "UI", show: bool, items: list[dict[str, Callable]]) -> None:
        super().__init__(ui)
        self.widget: QSplitter = QSplitter(QtCore.Qt.Orientation.Vertical)
        self.widget.setChildrenCollapsible(True)

        self.show = show
        self.items = items

    def load_items(self) -> None:
        if not self.items:
            return

        for item in self.items:
            itemtype = item.get("type", None)

            if itemtype == "Sceneform":
                columns = item.get("columns", None)
                if columns is None:
                    raise ValueError("Please setup config for Sceneform")
                self.sceneform = Sceneform(columns=columns)
                self.add(self.sceneform)

            if itemtype == "ObjectSetting":
                self.object_setting = ObjectSetting()
                self.add(self.object_setting)

        # Set equal sizes for all children
        child_count = self.widget.count()
        if child_count > 0:
            # Set each child to have equal size (1000 is arbitrary but proportional)
            equal_sizes = [1000] * child_count
            self.widget.setSizes(equal_sizes)
