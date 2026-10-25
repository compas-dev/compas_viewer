from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas_viewer.components.container import Container

from .mainwindow import MainWindow


class SideDock(Container):
    """Create a movable dock attached to a main window.

    Parameters
    ----------
    window
        Main window that owns the dock.

    """

    locations = {
        "left": Qt.DockWidgetArea.LeftDockWidgetArea,
        "right": Qt.DockWidgetArea.RightDockWidgetArea,
    }

    def __init__(self, window: MainWindow) -> None:
        super().__init__(container_type="scrollable")
        self.widget = QDockWidget()
        self.widget.setMinimumWidth(200)
        self.scroll = QScrollArea()
        self.scroll.setStyleSheet("QScrollArea { border: none; }")
        self.widget.setWidget(self.scroll)
        content = QWidget()
        self.scroll.setWidget(content)
        self.scroll.setWidgetResizable(True)
        self.layout = QVBoxLayout(content)
        self.layout.setAlignment(Qt.AlignTop)
        self.widget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.widget.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        window.widget.addDockWidget(self.locations["left"], self.widget)
