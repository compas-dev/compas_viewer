import sys
from typing import Callable
from typing import Optional

from PySide6.QtWidgets import QApplication

from compas_viewer.config import Config
from compas_viewer.configurations import ControllerConfig
from compas_viewer.controller import Controller
from compas_viewer.components.renderer import Renderer
from compas_viewer.configurations import RendererConfig
from compas_viewer.scene.scene import ViewerScene
from compas_viewer.singleton import Singleton
from compas_viewer.ui.ui import UI
from compas_viewer.qt import Timer


class Viewer(Singleton):
    def __init__(self, *args, **kwargs):
        self.app = QApplication(sys.argv)
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

    def on(self, interval: int, timeout: Optional[int] = None, frames: Optional[int] = None) -> Callable:
        """Decorator for callbacks of a dynamic drawing process.

        Parameters
        ----------
        interval : int
            Interval between subsequent calls to this function, in milliseconds.
        timeout : int, optional
            Timeout between subsequent calls to this function, in milliseconds.
        frames : int, optional
            The number of frames of the process.
            If no frame number is provided, the process continues until the viewer is closed.

        Returns
        -------
        Callable

        Notes
        -----
        The difference between `interval` and `timeout` is that the former indicates
        the time between subsequent calls to the callback,
        without taking into account the duration of the execution of the call,
        whereas the latter indicates a pause after the completed execution of the previous call,
        before starting the next one.

        Examples
        --------
        .. code-block:: python

            angle = math.radians(5)


            @viewer.on(interval=1000)
            def rotate(frame):
                obj.rotation = [0, 0, frame * angle]
                obj.update()

        """
        if (not interval and not timeout) or (interval and timeout):
            raise ValueError("Must specify either interval or timeout.")

        def outer(func: Callable):
            def renderer():
                func(self.frame_count)
                self.renderer.update()
                self.frame_count += 1
                if frames is not None and self.frame_count >= frames:
                    self.timer.stop()

            if interval:
                self.timer = Timer(interval=interval, callback=renderer)
            if timeout:
                self.timer = Timer(interval=timeout, callback=renderer, singleshot=True)

            self.frame_count = 0

        return outer
