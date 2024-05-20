from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6.QtWidgets import QDockWidget

from compas_viewer.base import Base


class SideDock(Base):
    def __init__(self) -> None:
        self.widget = None
        self.location = "left"
        self.show = False

        self.widget = QDockWidget()
        self.widget.setMinimumWidth(200)
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setStyleSheet("QScrollArea { border: none; }")
        self.widget.setWidget(self.scroll)
        content = QtWidgets.QWidget()
        self.scroll.setWidget(content)
        self.scroll.setWidgetResizable(True)
        self.layout = QtWidgets.QVBoxLayout(content)
        self.layout.setAlignment(QtCore.Qt.AlignTop)

    def lazy_init(self):
        self.widget.setVisible(self.show)

        locations = {
            "left": QtCore.Qt.LeftDockWidgetArea,
            "right": QtCore.Qt.RightDockWidgetArea,
            "top": QtCore.Qt.TopDockWidgetArea,
            "bottom": QtCore.Qt.BottomDockWidgetArea,
        }

        self.viewer.ui.window.addDockWidget(locations[self.location], self.widget)

    def add(self, widget):
        self.layout.addWidget(widget)
