from compas_viewer.base import Base

from .components.mainwindow import MainWindow
from .components.menubar import MenuBar
from .components.sidedock import SideDock
from .components.statusbar import StatusBar
from .components.toolbar import ToolBar
from .components.viewport import ViewPort


class UI(Base):
    def __init__(self) -> None:
        self.window = MainWindow()
        self.menubar = MenuBar(self.window)
        self.toolbar = ToolBar(self.window)
        self.statusbar = StatusBar(self.window)
        self.sidedock = SideDock(self.window)
        self.viewport = ViewPort(self.window)

        self.menubar.show = self.viewer.config.ui.menubar.show
        self.toolbar.show = self.viewer.config.ui.toolbar.show
        self.sidebar.show = self.viewer.config.ui.sidebar.show
        self.sidedock.show = self.viewer.config.ui.sidedock.show

    @property
    def sidebar(self):
        return self.viewport.sidebar

    def init(self):
        self.window.resize(self.viewer.config.window.width, self.viewer.config.window.height)
        self.window.widget.show()

        self.sidebar.update()
