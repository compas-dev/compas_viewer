from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6.QtWidgets import QDockWidget
from compas_viewer.components.container import Container


class SideDock(Container):
    locations = {
        "left": QtCore.Qt.DockWidgetArea.LeftDockWidgetArea,
        "right": QtCore.Qt.DockWidgetArea.RightDockWidgetArea,
    }

    def __init__(self) -> None:
        super().__init__(container_type="scrollable")
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
        self.widget.setAllowedAreas(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea | QtCore.Qt.DockWidgetArea.RightDockWidgetArea)
        self.widget.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
