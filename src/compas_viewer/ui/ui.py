from typing import TYPE_CHECKING

from .mainwindow import MainWindow
from .menubar import MenuBar
from .sidebar import SideBarRight
from .sidedock import SideDock
from .statusbar import SatusBar
from .toolbar import ToolBar
from .viewport import ViewPort

if TYPE_CHECKING:
    from compas_viewer import Viewer


class UI:
    def __init__(self, viewer: "Viewer") -> None:
        self.viewer = viewer
        self.window = MainWindow(title=self.viewer.config.window.title)

        self.menubar = MenuBar(
            self,
            items=self.viewer.config.ui.menubar.items,
        )
        self.statusbar = SatusBar(
            self,
            show=self.viewer.config.ui.statusbar.show,
        )
        self.toolbar = ToolBar(
            self,
            items=self.viewer.config.ui.toolbar.items,
            show=self.viewer.config.ui.toolbar.show,
        )
        self.sidebar = SideBarRight(
            self,
            show=self.viewer.config.ui.sidebar.show,
            items=self.viewer.config.ui.sidebar.items,
        )
        self.viewport = ViewPort(
            self,
            self.viewer.renderer,
            self.sidebar,
        )
        self.sidedock = SideDock(
            self,
            show=self.viewer.config.ui.sidedock.show,
        )
        # TODO: find better solution to transient window
        self.sidebar.load_items()
        self.window.widget.setCentralWidget(self.viewport.widget)
        self.window.widget.addDockWidget(SideDock.locations["left"], self.sidedock.widget)

    def init(self):
        self.resize(self.viewer.config.window.width, self.viewer.config.window.height)
        self.window.widget.show()
        self.sidebar.update()

    def resize(self, w: int, h: int) -> None:
        self.window.widget.resize(w, h)
        rect = self.viewer.app.primaryScreen().availableGeometry()
        x = 0.5 * (rect.width() - w)
        y = 0.5 * (rect.height() - h)
        self.window.widget.setGeometry(x, y, w, h)
