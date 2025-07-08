from PySide6.QtWidgets import QMainWindow

from compas_viewer.components.component import Component


class MainWindow(Component):
    def __init__(self):
        super().__init__()
        self.widget = QMainWindow()
        self.title = self.viewer.config.window.title

    @property
    def title(self):
        return self.widget.windowTitle()

    @title.setter
    def title(self, title: str):
        self._title = title
        self.widget.setWindowTitle(title)
