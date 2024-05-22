from compas_viewer.base import Base

from .mainwindow import MainWindow
from .menubar import MenuBar
from .sidedock import SideDock
from .statusbar import SatusBar
from .toolbar import ToolBar
from .viewport import ViewPort


class UI(Base):
    def __init__(self) -> None:
        self.window = MainWindow()
        self.menubar = MenuBar()
        self.statusbar = SatusBar()
        self.toolbar = ToolBar()
        self.viewport = ViewPort()
        self.sidedock = SideDock()

    def lazy_init(self):
        self.window.lazy_init()
        self.menubar.lazy_init()
        self.statusbar.lazy_init()
        self.toolbar.lazy_init()
        self.viewport.lazy_init()
        self.sidedock.lazy_init()

    def show(self):
        self.resize(self.viewer.config.window.width, self.viewer.config.window.height)
        self.window.show()

    def resize(self, w: int, h: int) -> None:
        self.window.resize(w, h)
        rect = self.viewer.app.primaryScreen().availableGeometry()
        x = 0.5 * (rect.width() - w)
        y = 0.5 * (rect.height() - h)
        self.window.setGeometry(x, y, w, h)
