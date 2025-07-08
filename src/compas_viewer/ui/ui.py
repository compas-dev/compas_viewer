from typing import TYPE_CHECKING

from .mainwindow import MainWindow
from .menubar import MenuBar
from .sidebar import SideBarRight
from .sidedock import SideDock
from .statusbar import StatusBar
from .toolbar import ToolBar
from .viewport import ViewPort

if TYPE_CHECKING:
    from compas_viewer import Viewer


class UI:
    def __init__(self, viewer: "Viewer") -> None:
        self.viewer = viewer
        self.window = MainWindow(title=self.viewer.config.window.title)
        self.menubar = MenuBar(self.window, items=self.viewer.config.ui.menubar.items)
        self.toolbar = ToolBar(self.window, items=self.viewer.config.ui.toolbar.items)
        self.statusbar = StatusBar(self.window)
        self.sidebar = SideBarRight(items=self.viewer.config.ui.sidebar.items)
        self.sidedock = SideDock()
        self.viewport = ViewPort(
            self,
            self.viewer.renderer,
            self.sidebar,
        )

        self.window.widget.setCentralWidget(self.viewport.widget)
        self.window.widget.addDockWidget(SideDock.locations["left"], self.sidedock.widget)

    def init(self):
        self.resize(self.viewer.config.window.width, self.viewer.config.window.height)
        self.window.widget.show()

        self.menubar.add_menu()
        self.menubar.show = self.viewer.config.ui.menubar.show
        self.toolbar.show = self.viewer.config.ui.toolbar.show
        self.sidebar.show = self.viewer.config.ui.sidebar.show
        self.sidedock.show = self.viewer.config.ui.sidedock.show

    def resize(self, w: int, h: int) -> None:
        self.window.widget.resize(w, h)
        rect = self.viewer.app.primaryScreen().availableGeometry()
        x = 0.5 * (rect.width() - w)
        y = 0.5 * (rect.height() - h)
        self.window.widget.setGeometry(x, y, w, h)
