import pathlib
from typing import Callable
from typing import Optional
from typing import Union

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


def set_icon_path(icon_name: str) -> str:
    path = QtGui.QIcon(str(pathlib.Path(__file__).parent.parent / "icons" / icon_name))
    return path


class Button(QtWidgets.QPushButton):
    def __init__(
        self,
        text: Optional[str] = None,
        icon_path: Optional[Union[str, pathlib.Path]] = None,
        tooltip: Optional[str] = None,
        action: Optional[Callable[[], None]] = None,
        parent=None,
    ):
        super().__init__()
        if text:
            self.setText(text)
        if icon_path:
            self.setIcon(QtGui.QIcon(set_icon_path(icon_path)))
        if tooltip:
            self.setToolTip(tooltip)
        if action:
            self.clicked.connect(action)
        self.setIconSize(QtCore.QSize(17, 17))
