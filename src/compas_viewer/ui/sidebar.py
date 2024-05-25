from typing import TYPE_CHECKING

from PySide6 import QtCore
from PySide6 import QtWidgets

if TYPE_CHECKING:
    from .ui import UI


class SideBarRight:
    def __init__(self, ui: "UI", show: bool = True) -> None:
        self.ui = ui
        self.widget = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.widget.setChildrenCollapsible(True)
        self.widget.setVisible(show)

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
