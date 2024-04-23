from typing import TYPE_CHECKING
from .main_window import MainWindow
from .menu_bar import MenuBar
from .status_bar import SatusBar
from .tool_bar import ToolBar
from .view_port import ViewPort

if TYPE_CHECKING:
    from compas_viewer.main import Viewer

class UI:
    def __init__(self, viewer: "Viewer") -> None:
        
        self.viewer = viewer

        self.window = MainWindow(self)
        self.menubar = MenuBar(self)
        self.statusbar = SatusBar(self)
        self.toolbar = ToolBar(self)
        self.viewport = ViewPort(self)

    def init(self):
        width = self.viewer.config.window.width
        height = self.viewer.config.window.height
        self.resize(width, height)

    def show(self):
        self.window.show()

    def resize(self, w: int, h: int) -> None:
        self.window.resize(w, h)
        rect = self.viewer.app.primaryScreen().availableGeometry()
        x = 0.5 * (rect.width() - w)
        y = 0.5 * (rect.height() - h)
        self.window.setGeometry(x, y, w, h)