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

        self._unit = None
        self.unit = self.viewer.config.unit

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, unit: str):
        if self.viewer.running:
            raise NotImplementedError("Changing the unit after the viewer is running is not yet supported.")
        if unit != self._unit:
            previous_scale = self.viewer.config.camera.scale
            if unit == "m":
                self.viewer.config.renderer.gridsize = (10.0, 10, 10.0, 10)
                self.renderer.camera.scale = 1.0
            elif unit == "cm":
                self.viewer.config.renderer.gridsize = (1000.0, 10, 1000.0, 10)
                self.renderer.camera.scale = 100.0
            elif unit == "mm":
                self.viewer.config.renderer.gridsize = (10000.0, 10, 10000.0, 10)
                self.renderer.camera.scale = 1000.0
            else:
                raise ValueError(f"Invalid unit: {unit}. Valid units are 'm', 'cm', 'mm'.")
            self.renderer.camera.distance *= self.renderer.camera.scale / previous_scale

        self._unit = unit
