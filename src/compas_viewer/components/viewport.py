from typing import cast

from PySide6.QtWidgets import QSplitter

from compas_viewer.components.component import Component
from compas_viewer.config import Unit
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
        self._unit: Unit | None = None
        self.widget.addWidget(self.renderer)
        self.unit = self.viewer.config.unit
        self.sidebar = SideBarRight(self)
        self.widget.addWidget(self.sidebar.widget)
        sidebar_width = self.viewer.config.ui.sidebar.width
        self.widget.setSizes([self.viewer.config.window.width - sidebar_width, sidebar_width])
        self.widget.setStretchFactor(0, 1)
        self.widget.setStretchFactor(1, 0)
        window.widget.setCentralWidget(self.widget)
        self.viewer.state.changed.connect(self._on_state_changed)

    @property
    def unit(self) -> Unit:
        """Unit: Display unit controlling the camera and grid scale."""
        return cast(Unit, self._unit)

    @unit.setter
    def unit(self, unit: Unit) -> None:
        if unit != self._unit:
            previous_scale = self.renderer.camera.scale
            if unit == "m":
                self.viewer.state.set("renderer.gridsize", (10.0, 10, 10.0, 10))
                self.renderer.camera.scale = 1.0
            elif unit == "cm":
                self.viewer.state.set("renderer.gridsize", (1000.0, 10, 1000.0, 10))
                self.renderer.camera.scale = 100.0
            elif unit == "mm":
                self.viewer.state.set("renderer.gridsize", (10000.0, 10, 10000.0, 10))
                self.renderer.camera.scale = 1000.0
            else:
                raise ValueError(f"Invalid unit: {unit}. Valid units are 'm', 'cm', 'mm'.")
            self.renderer.camera.distance *= self.renderer.camera.scale / previous_scale
            self.viewer.state.set("camera.scale", self.renderer.camera.scale)

        self._unit = unit
        self.viewer.state.set("unit", unit)
        if self.viewer.running:
            self.renderer.rebuild_grid()
            self.renderer.update()

    def _on_state_changed(self, path: str, value: object) -> None:
        """Apply unit changes originating from another UI surface."""
        if path == "unit" and value != self._unit:
            self.unit = cast(Unit, value)
