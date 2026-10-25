from PySide6.QtWidgets import QLabel

from compas_viewer.components.component import Component

from .mainwindow import MainWindow


class StatusBar(Component):
    """Create the status bar owned by a main window.

    Parameters
    ----------
    window
        Main window that owns the status bar.

    """

    def __init__(self, window: MainWindow) -> None:
        super().__init__()
        self.widget = window.widget.statusBar()
        self.widget.addWidget(QLabel(text="Ready..."))
