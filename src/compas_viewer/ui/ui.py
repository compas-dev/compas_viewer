from compas_viewer.components.component_manager import ComponentsManager

from .mainwindow import MainWindow
from .menubar import MenuBar
from .statusbar import SatusBar
from .toolbar import ToolBar
from .viewport import ViewPort


class UI:
    def __init__(self) -> None:
        self.components_manager = ComponentsManager()
        self.window = MainWindow()
        self.menubar = MenuBar()
        self.statusbar = SatusBar()
        self.toolbar = ToolBar()
        self.viewport = ViewPort()

    @property
    def viewer(self):
        from compas_viewer.viewer import Viewer

        return Viewer()

    def lazy_init(self):
        width = self.viewer.config.window.width
        height = self.viewer.config.window.height

        self.resize(width, height)
        self.components_manager.setup_manager()
        self.window.setup_window()
        self.menubar.setup_menu()
        self.statusbar.setup_status_bar()
        self.toolbar.setup_tool_bar()
        self.viewport.setup_view_port()
        self.viewer.renderer.camera.setup_camera()

    def show(self):
        self.window.show()

    def resize(self, w: int, h: int) -> None:
        self.window.resize(w, h)
        rect = self.viewer.app.primaryScreen().availableGeometry()
        x = 0.5 * (rect.width() - w)
        y = 0.5 * (rect.height() - h)
        self.window.setGeometry(x, y, w, h)
