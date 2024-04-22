import pathlib
from typing import TYPE_CHECKING
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui

if TYPE_CHECKING:
    from .ui import UI

def test_action():
    print("test action...")

class ToolBar:
    def __init__(self, ui: "UI") -> None:
        self.ui = ui
        self.config = ui.viewer.config.ui.toolbar
        self.window = self.ui.window
        self.widget = self.window.addToolBar("Tools")

        self.init_toolbar()

        icon = QtGui.QIcon(
            str(pathlib.Path(__file__).parent.parent / "icons" / "zoom_selected.svg")
        )
        button = QtWidgets.QPushButton()
        button.setToolTip("Zoom")
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(12, 12))
        button.clicked.connect(test_action)

        self.widget.addWidget(button)
    
    def init_toolbar(self) -> None:
        self.widget.setMovable(False)
        self.widget.setObjectName("Tools")
        self.widget.setHidden(not self.config.show)