from typing import TYPE_CHECKING
from typing import Callable

from PySide6 import QtCore
from PySide6.QtWidgets import QSplitter

from compas_viewer.components import Sceneform

if TYPE_CHECKING:
    from .ui import UI


class SideBarRight:
    def __init__(self, ui: "UI", show: bool, items: list[dict[str, Callable]]) -> None:
        self.ui = ui
        self.widget = QSplitter(QtCore.Qt.Orientation.Vertical)
        self.widget.setChildrenCollapsible(True)
        self.show = show
        self.items = items

    def add_items(self, items: list[dict[str, Callable]], parent: QSplitter) -> None:
        if not items:
            return

        for item in items:
            itemtype = item.get("type", None)
            action = item.get("action", None)

            if itemtype == "Sceneform":
                parent.addWidget(Sceneform(self.ui.viewer.scene, action))

    def update(self):
        # TODO: find better solution for transient window
        self.add_items(self.items, self.widget)
        self.widget.update()
        for widget in self.widget.children():
            widget.update()

    @property
    def show(self):
        return self.widget.isVisible()

    @show.setter
    def show(self, value: bool):
        if value:
            self.widget.setVisible(True)
        elif not value:
            self.widget.setHidden(True)
