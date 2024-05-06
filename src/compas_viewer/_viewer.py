import sys

from PySide6.QtWidgets import QApplication

from compas_viewer.components.renderer import Renderer
from compas_viewer.config import Config
from compas_viewer.configurations import ControllerConfig
from compas_viewer.configurations import RendererConfig
from compas_viewer.controller import Controller
from compas_viewer.scene.scene import ViewerScene
from compas_viewer.ui.ui import UI


class Viewer:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Viewer, cls).__new__(cls)
            cls._is_initialised = False
        return cls._instance

    def __init__(self, *args, **kwargs):
        if not self._is_initialised:
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()

            self.config = Config.from_json("src/compas_viewer/config.json")
            self.scene = ViewerScene(name="ViewerScene", context="Viewer")
            # TODO(pitsai): combine config file
            self.renderer = Renderer(RendererConfig.from_default())
            self.controller = Controller(ControllerConfig.from_default())
            self.ui = UI()
            self._is_initialised = True

    def show(self):
        self.ui.lazy_init()
        self.ui.show()
        self.app.exec()
