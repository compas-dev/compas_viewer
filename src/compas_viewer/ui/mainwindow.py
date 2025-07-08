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

    def resize(self, w: int, h: int) -> None:
        self.widget.resize(w, h)
        rect = self.viewer.app.primaryScreen().availableGeometry()
        x = 0.5 * (rect.width() - w)
        y = 0.5 * (rect.height() - h)
        self.widget.setGeometry(x, y, w, h)
