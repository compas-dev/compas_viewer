from typing import TYPE_CHECKING

from PySide6 import QtCore
from PySide6 import QtWidgets

from compas_viewer.components.objectsetting import ObjectSetting

if TYPE_CHECKING:
    from .ui import UI


def is_layout_empty(layout):
    return layout.count() == 0


class SideBarRight:
    def __init__(self, ui: "UI", show: bool = True) -> None:
        self.ui = ui
        self.widget = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.widget.setChildrenCollapsible(True)
        self.show = show

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
