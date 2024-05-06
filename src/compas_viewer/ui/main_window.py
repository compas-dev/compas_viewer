from typing import Optional

from PySide6 import QtWidgets
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QWidget


class MainWindow(QMainWindow):
    @property
    def viewer(self):
        from compas_viewer.main import Viewer

        return Viewer()

    def setup_window(self):
        self.set_window_title()
        self.set_window_central()

    def set_window_title(self, title: Optional[str] = None) -> None:
        if title is None:
            title = self.viewer.config.window.title
        self.setWindowTitle(title)

    def set_window_central(self) -> None:
        layout = QtWidgets.QHBoxLayout()
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
