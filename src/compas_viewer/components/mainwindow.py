from PySide6.QtWidgets import QMainWindow

from compas_viewer.components.component import Component


class MainWindow(Component):
    """Wrap the viewer's main Qt window."""

    def __init__(self) -> None:
        super().__init__()
        self.widget = QMainWindow()
        self.title = self.viewer.config.window.title

    @property
    def title(self) -> str:
        """str: The main-window title."""
        return self.widget.windowTitle()

    @title.setter
    def title(self, title: str) -> None:
        self._title = title
        self.widget.setWindowTitle(title)

    def resize(self, w: int, h: int) -> None:
        """Resize the main window.

        Parameters
        ----------
        w
            Window width in pixels.
        h
            Window height in pixels.

        """
        self.widget.resize(w, h)
        rect = self.viewer.app.primaryScreen().availableGeometry()
        x = 0.5 * (rect.width() - w)
        y = 0.5 * (rect.height() - h)
        self.widget.setGeometry(x, y, w, h)
