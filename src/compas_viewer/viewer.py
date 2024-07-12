import os
import sys
from typing import Callable
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from compas.scene import Scene
from compas_viewer import HERE
from compas_viewer.config import Config
from compas_viewer.events import EventManager
from compas_viewer.mouse import Mouse
from compas_viewer.renderer import Renderer
from compas_viewer.scene import ViewerScene
from compas_viewer.singleton import Singleton
from compas_viewer.ui import UI


class Viewer(Singleton):
    def __init__(self, config: Optional[Config] = None, **kwargs):
        self.running = False
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("COMPAS Viewer")
        self.app.setApplicationDisplayName("COMPAS Viewer")
        self.app.setWindowIcon(QIcon(os.path.join(HERE, "assets", "icons", "compas_icon_white.png")))

        self._scene = None
        self._unit = "m"

        self.config = config or Config()
        self.timer = QTimer()
        self.mouse = Mouse()

        self.eventmanager = EventManager(self)

        # renderer should be part of UI
        self.renderer = Renderer(self)
        self.ui = UI(self)
        self.unit = self.config.unit

    @property
    def scene(self) -> ViewerScene:
        if self._scene is None:
            self._scene = ViewerScene()
        return self._scene

    @scene.setter
    def scene(self, scene: Scene):
        self._scene = ViewerScene.__from_data__(scene.__data__)
        if self.running:
            for obj in self._scene.objects:
                obj.init()

    @property
    def unit(self) -> str:
        return self._unit

    @unit.setter
    def unit(self, unit: str):
        if self.running:
            raise NotImplementedError("Changing the unit after the viewer is running is not yet supported.")
        if unit != self._unit:
            previous_scale = self.config.camera.scale
            if unit == "m":
                self.config.renderer.gridsize = (10.0, 10, 10.0, 10)
                self.renderer.camera.scale = 1.0
            elif unit == "cm":
                self.config.renderer.gridsize = (1000.0, 10, 1000.0, 10)
                self.renderer.camera.scale = 100.0
            elif unit == "mm":
                self.config.renderer.gridsize = (10000.0, 10, 10000.0, 10)
                self.renderer.camera.scale = 1000.0
            else:
                raise ValueError(f"Invalid unit: {unit}. Valid units are 'm', 'cm', 'mm'.")
            self.renderer.camera.distance *= self.renderer.camera.scale / previous_scale

        self._unit = unit

    def show(self):
        self.running = True
        self.ui.init()
        self.app.exec()

    def on(self, interval: int, frames: Optional[int] = None) -> Callable:
        """Decorator for callbacks of a dynamic drawing process with fixed intervals.

        Parameters
        interval : int
            Interval between subsequent calls to this function, in milliseconds.
        frames : int, optional
            The number of frames of the process.
            If no frame number is provided, the process continues until the viewer is closed.

        Returns
        -------
        Callable
        """
        self.frame_count = 0

        def decorator(func: Callable):
            def wrapper():
                if frames is not None and self.frame_count >= frames:
                    self.timer.stop()
                    return
                func(self.frame_count)
                self.frame_count += 1
                self.renderer.update()

            self.timer.timeout.connect(wrapper)
            self.timer.start(interval)
            return func

        return decorator
