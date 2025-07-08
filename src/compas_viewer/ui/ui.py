from compas_viewer.base import Base

from .mainwindow import MainWindow
from .menubar import MenuBar
from .sidebar import SideBarRight
from .sidedock import SideDock
from .statusbar import StatusBar
from .toolbar import ToolBar
from .viewport import ViewPort


class UI(Base):
    def __init__(self) -> None:
        self.window = MainWindow()
        self.menubar = MenuBar(self.window)
        self.toolbar = ToolBar(self.window)
        self.statusbar = StatusBar(self.window)
        self.sidedock = SideDock(self.window)
        self.viewport = ViewPort(self.window)

    @property
    def sidebar(self):
        return self.viewport.sidebar

    def init(self):
        self.resize(self.viewer.config.window.width, self.viewer.config.window.height)
        self.window.widget.show()

        self.menubar.add_menu()
        self.menubar.show = self.viewer.config.ui.menubar.show
        self.toolbar.show = self.viewer.config.ui.toolbar.show
        self.sidebar.show = self.viewer.config.ui.sidebar.show
        self.sidedock.show = self.viewer.config.ui.sidedock.show

        self.sidebar.update()

    def resize(self, w: int, h: int) -> None:
        self.window.widget.resize(w, h)
        rect = self.viewer.app.primaryScreen().availableGeometry()
        x = 0.5 * (rect.width() - w)
        y = 0.5 * (rect.height() - h)
        self.window.widget.setGeometry(x, y, w, h)
