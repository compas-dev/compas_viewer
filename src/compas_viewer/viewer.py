import sys

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
        self.config = Config()
        self.scene = ViewerScene()
        # TODO(pitsai): combine config file
        # self.renderer = Renderer(RendererConfig.from_default())
        self.controller = Controller(ControllerConfig.from_default())
        self.ui = UI()

    def show(self):
        self.ui.lazy_init()
        self.ui.show()
        self.app.exec()
