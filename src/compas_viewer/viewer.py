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


# this should not be a singleton
# because it might be created somewhere else too early
# without the custom configuration
class Viewer(Singleton):
    def __init__(self, config: Config = None, show_grid: bool = True, **kwargs):
        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(QIcon(os.path.join(HERE, "icons", "compas_icon_white.png")))

        self.timer = QTimer()

        self.config = config or Config()
        self.config.renderer.show_grid = show_grid

        # otherwise this results in a circular import
        # both of these should be removed from this __init__
        # renderer needs to go to view3d
        # controller needs to be refactored to eventmanager
        self.renderer = Renderer(self.config)
        self.eventmanager = EventManager(self)
        self.mouse = Mouse()

        self.ui = UI()
        self._scene = None

    @property
    def scene(self) -> ViewerScene:
        if self._scene is None:
            self._scene = ViewerScene()
        return self._scene

    @scene.setter
    def scene(self, scene: Scene):
        self._scene = ViewerScene.__from_data__(scene.__data__)

    def show(self):
        # none of these lazy inits should be necessary
        # it just covers up for a design flaw
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
