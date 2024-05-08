from compas_viewer.base import Base
from compas_viewer.components.component_manager import ComponentsManager

from .mainwindow import MainWindow
from .menubar import MenuBar
from .statusbar import SatusBar
from .toolbar import ToolBar
from .viewport import ViewPort


class UI(Base):
    def __init__(self) -> None:
        self.components_manager = ComponentsManager()
        self.window = MainWindow()
        self.menubar = MenuBar()
        self.statusbar = SatusBar()
        self.toolbar = ToolBar()
        self.viewport = ViewPort()

    def lazy_init(self):
        width = self.viewer.config.window.width
        height = self.viewer.config.window.height

        self.resize(width, height)
        self.components_manager.lazy_init()
        self.window.lazy_init()
        self.menubar.lazy_init()
        self.statusbar.lazy_init()
        self.toolbar.lazy_init()
        self.viewport.lazy_init()
        self.viewer.renderer.camera.lazy_init()

    def show(self):
        self.window.show()

    def resize(self, w: int, h: int) -> None:
        self.window.resize(w, h)
        rect = self.viewer.app.primaryScreen().availableGeometry()
        x = 0.5 * (rect.width() - w)
        y = 0.5 * (rect.height() - h)
        self.window.setGeometry(x, y, w, h)
