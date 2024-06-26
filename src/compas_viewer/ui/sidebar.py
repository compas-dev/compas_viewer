from typing import TYPE_CHECKING
from typing import Callable

from PySide6 import QtCore
from PySide6.QtWidgets import QSplitter

from compas_viewer.components import Sceneform
from compas_viewer.components.objectsetting import ObjectSetting

if TYPE_CHECKING:
    from .ui import UI


def is_layout_empty(layout):
    # one is the label widget
    return layout.count() == 1


class SideBarRight:
    def __init__(self, ui: "UI", show: bool, items: list[dict[str, Callable]]) -> None:
        self.ui = ui
        self.widget = QSplitter(QtCore.Qt.Orientation.Vertical)
        self.widget.setChildrenCollapsible(True)
        self.show = show
        self.items = items

    def add_items(self) -> None:
        if not self.items:
            return

        for item in self.items:
            itemtype = item.get("type", None)

            if itemtype == "Sceneform":
                columns = item.get("columns", None)
                if columns is not None:
                    self.widget.addWidget(Sceneform(columns))
                else:
                    raise ValueError("Columns not provided for Sceneform")

    def update(self):
        self.widget.update()
        for widget in self.widget.children():
            widget.update()
            if not self.show_widget and isinstance(widget, ObjectSetting):
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
