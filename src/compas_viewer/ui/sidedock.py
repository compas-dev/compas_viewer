from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6.QtWidgets import QDockWidget


class SideDock:
    locations = {
        "left": QtCore.Qt.DockWidgetArea.LeftDockWidgetArea,
        "right": QtCore.Qt.DockWidgetArea.RightDockWidgetArea,
    }

    def __init__(self) -> None:
        self.widget = None
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
        self.widget.setVisible(False)

    @property
    def show(self):
        return self.widget.isVisible()

    @show.setter
    def show(self, value: bool):
        self.widget.setVisible(value)

    def add(self, widget):
        self.layout.addWidget(widget)
