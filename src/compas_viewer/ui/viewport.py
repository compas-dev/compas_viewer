from PySide6.QtWidgets import QSplitter

from compas_viewer.components.component import Component
from compas_viewer.renderer import Renderer

from .mainwindow import MainWindow
from .sidebar import SideBarRight


class ViewPort(Component):
    def __init__(self, window: MainWindow):
        super().__init__()
        self.widget = QSplitter()
        self.renderer = Renderer()
        self.widget.addWidget(self.renderer)
        self.sidebar = SideBarRight()
        self.widget.addWidget(self.sidebar.widget)
        self.widget.setSizes([800, 200])
        window.widget.setCentralWidget(self.widget)
