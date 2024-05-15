import sys
from typing import Callable
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from compas_viewer.components.renderer import Renderer
from compas_viewer.config import Config
from compas_viewer.configurations import ControllerConfig
from compas_viewer.configurations import RendererConfig
from compas_viewer.controller import Controller
from compas_viewer.scene.scene import ViewerScene
from compas_viewer.singleton import Singleton
from compas_viewer.ui.ui import UI


class Viewer(Singleton):
    def __init__(self, *args, **kwargs):
        self.app = QApplication(sys.argv)
        self.timer = QTimer()
        self.config = Config()
        self.scene = ViewerScene()
        # TODO(pitsai): combine config file
        self.renderer = Renderer(RendererConfig.from_default())
        self.controller = Controller(ControllerConfig.from_default())
        self.ui = UI()

    def show(self):
        self.ui.lazy_init()
        self.ui.show()
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
