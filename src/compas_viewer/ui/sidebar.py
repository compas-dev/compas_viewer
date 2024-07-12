from typing import TYPE_CHECKING
from typing import Callable

from PySide6 import QtCore
from PySide6.QtWidgets import QSplitter

from compas_viewer.components import Sceneform
from compas_viewer.components.objectsetting import ObjectSetting

if TYPE_CHECKING:
    from .ui import UI


class SideBarRight:
    def __init__(self, ui: "UI", show: bool, items: list[dict[str, Callable]]) -> None:
        self.ui = ui
        self.widget = QSplitter(QtCore.Qt.Orientation.Vertical)
        self.widget.setChildrenCollapsible(True)
        self.show = show
        self.hide_widget = True
        self.items = items

    def add_items(self) -> None:
        if not self.items:
            return

        for item in self.items:
            itemtype = item.get("type", None)

            if itemtype == "Sceneform":
                columns = item.get("columns", None)
                if columns is None:
                    raise ValueError("Please setup config for Sceneform")
                self.sceneform = Sceneform(columns=columns)
                self.widget.addWidget(self.sceneform)

            elif itemtype == "ObjectSetting":
                items = item.get("items", None)
                if items is None:
                    raise ValueError("Please setup config for ObjectSetting")
                self.object_setting = ObjectSetting(viewer=self.ui.viewer, items=items)
                self.widget.addWidget(self.object_setting)

        self.show_sceneform = True
        self.show_objectsetting = True

    def update(self):
        self.widget.update()
        for widget in self.widget.children():
            widget.update()

    @property
    def show(self):
        return self.widget.isVisible()

    @show.setter
    def show(self, value: bool):
        self.widget.setVisible(value)

    @property
    def show_sceneform(self):
        return self.sceneform.isVisible()

    @show_sceneform.setter
    def show_sceneform(self, value: bool):
        self.sceneform.setVisible(value)

    @property
    def show_objectsetting(self):
        return self.object_setting.isVisible()

    @show_objectsetting.setter
    def show_objectsetting(self, value: bool):
        self.object_setting.setVisible(value)
