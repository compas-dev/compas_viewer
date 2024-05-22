from PySide6 import QtWidgets
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QWidget

from compas_viewer.base import Base


class MainWindow(QMainWindow, Base):
    def lazy_init(self):
        title = self.viewer.config.window.title
        self.setWindowTitle(title)
        layout = QtWidgets.QHBoxLayout()
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
