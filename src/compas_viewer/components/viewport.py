from PySide6.QtWidgets import QSplitter

from compas_viewer.components.component import Component
from compas_viewer.renderer import Renderer

from .mainwindow import MainWindow
from .sidebar import SideBarRight


class ViewPort(Component):
    """Combine the renderer and right sidebar in the main window.

    Parameters
    ----------
    window
        Main window that receives the viewport as its central widget.

    """

    def __init__(self, window: MainWindow) -> None:
        super().__init__()
        self.widget = QSplitter()
        self.renderer = Renderer()
        self.widget.addWidget(self.renderer)
        self.sidebar = SideBarRight(self)
        self.widget.addWidget(self.sidebar.widget)
        sidebar_width = self.viewer.config.ui.sidebar.width
        self.widget.setSizes([self.viewer.config.window.width - sidebar_width, sidebar_width])
        self.widget.setStretchFactor(0, 1)
        self.widget.setStretchFactor(1, 0)
        window.widget.setCentralWidget(self.widget)
