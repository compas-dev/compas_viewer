from typing import TYPE_CHECKING
from typing import Callable

from PySide6 import QtCore
from PySide6.QtWidgets import QSplitter

from compas_viewer.components import Sceneform
from compas_viewer.components import Treeform
from compas_viewer.components.objectsetting import ObjectSetting

if TYPE_CHECKING:
    from .ui import UI


def is_layout_empty(layout):
    return layout.count() == 1


class SideBarRight:
    def __init__(self, ui: "UI", show: bool, items: list[dict[str, Callable]]) -> None:
        self.ui = ui
        self.widget = QSplitter(QtCore.Qt.Orientation.Vertical)
        self.widget.setChildrenCollapsible(True)
        self.show = show
        self.hide_widget = True
        self.items = items
        self.sceneform = None

    def add_items(self) -> None:
        if not self.items:
            return

        for item in self.items:
            itemtype = item.get("type", None)

            if itemtype == "Sceneform":
                columns = item.get("columns", None)
                if columns is None:
                    raise ValueError("Please setup config for Sceneform")
                self.widget.addWidget(Sceneform(columns=columns))

            elif itemtype == "ObjectSetting":
                items = item.get("items", None)
                if items is None:
                    raise ValueError("Please setup config for ObjectSetting")
                self.widget.addWidget(ObjectSetting(viewer=self.ui.viewer, items=items))

    def update(self):
        self.widget.update()
        for widget in self.widget.children():
            widget.update()
            if isinstance(widget, ObjectSetting):
                if is_layout_empty(widget.layout) and self.hide_widget:
                    widget.hide()
                else:
                    widget.show()

    @property
    def show(self):
        return self.widget.isVisible()

    @show.setter
    def show(self, value: bool):
        if value:
            self.widget.setVisible(True)
        elif not value:
            self.widget.setHidden(True)
