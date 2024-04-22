import pathlib
from typing import Callable, TYPE_CHECKING
from PySide6 import QtCore, QtWidgets, QtGui

ICON_PATH = QtGui.QIcon(
            str(pathlib.Path(__file__).parent.parent / "icons" / "zoom_selected.svg")
        )

class ButtonFactory(QtWidgets.QPushButton):
    def __init__(self, icon_path: str, tooltip: str, action: Callable[[], None], parent=None):
        super().__init__(parent)
        self.setIcon(QtGui.QIcon(icon_path))
        self.setToolTip(tooltip)
        self.setIconSize(QtCore.QSize(12, 12))
        self.clicked.connect(action)