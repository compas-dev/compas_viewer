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
    return layout.count() == 0


class SideBarRight:
    def __init__(self, ui: "UI", show: bool, items: list[dict[str, Callable]]) -> None:
        self.ui = ui
        self.widget = QSplitter(QtCore.Qt.Orientation.Vertical)
        self.widget.setChildrenCollapsible(True)
        self.show = show
        self.items = items
        self.sceneform = None

    def add_items(self) -> None:
        if not self.items:
            return

        for item in self.items:
            itemtype = item.get("type", None)

            if itemtype == "Sceneform":
                columns = item.get("columns", None)
                callback = item.get("callback", None)
                if columns is None:
                    raise ValueError("Columns not provided for Sceneform")
                self.sceneform = Sceneform(columns, callback=callback)
                self.widget.addWidget(self.sceneform)

            elif itemtype == "Treeform":
                item.pop("type")
                self.widget.addWidget(Treeform(**item))

    def update(self):
        self.widget.update()
        for widget in self.widget.children():
            widget.update()
            if isinstance(widget, ObjectSetting):
                if is_layout_empty(widget.layout):
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
