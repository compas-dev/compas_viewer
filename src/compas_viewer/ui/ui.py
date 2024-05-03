from .main_window import MainWindow
from .menu_bar import MenuBar
from .status_bar import SatusBar
from .tool_bar import ToolBar
from .view_port import ViewPort

class UI:
    def __init__(self) -> None:

        self.window = MainWindow()
        self.menubar = MenuBar()
        self.statusbar = SatusBar()
        self.toolbar = ToolBar()
        self.viewport = ViewPort()

    @property
    def viewer(self):
        from compas_viewer.main import Viewer
        return Viewer()
    
    def lazy_init(self):
        width = self.viewer.config.window.width
        height = self.viewer.config.window.height
        
        self.resize(width, height)
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
