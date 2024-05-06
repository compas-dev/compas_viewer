import pathlib
from typing import Callable

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


def set_icon_path(icon_name: str) -> str:
    path = QtGui.QIcon(
            str(pathlib.Path(__file__).parent.parent / "icons" / icon_name)
        ) 
    return path

class ButtonFactory(QtWidgets.QPushButton):
    def __init__(self, icon_name: str, tooltip: str, action: Callable[[], None], parent=None):
        super().__init__(parent)
        self.setIcon(QtGui.QIcon(set_icon_path(icon_name)))
        self.setToolTip(tooltip)
        self.setIconSize(QtCore.QSize(12, 12))
        self.clicked.connect(action)