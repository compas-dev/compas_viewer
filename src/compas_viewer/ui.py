from compas_viewer.base import Base

from .components.mainwindow import MainWindow
from .components.menubar import MenuBar
from .components.sidebar import SideBarRight
from .components.sidedock import SideDock
from .components.statusbar import StatusBar
from .components.toolbar import ToolBar
from .components.viewersettings import ViewerSettings
from .components.viewport import ViewPort


class UI(Base):
    """Compose and initialize the Viewer's owned Qt interface.

    The viewport embeds the Scene, Data, and Annotations content sidebar.
    Viewer-wide Camera, Display, and Grid and Units controls live in the
    separate reusable `settings` window.

    """

    def __init__(self) -> None:
        """Construct the main interface and the initially hidden settings window."""
        self.window = MainWindow()
        self.menubar = MenuBar(self.window)
        self.toolbar = ToolBar(self.window)
        self.statusbar = StatusBar(self.window)
        self.sidedock = SideDock(self.window)
        self.viewport = ViewPort(self.window)
        self._settings = ViewerSettings(self.window, self.viewport)
        self.menubar.bind_sidebar(self.sidebar)

        self.menubar.show = self.viewer.config.ui.menubar.show
        self.toolbar.show = self.viewer.config.ui.toolbar.show
        self.statusbar.show = self.viewer.config.ui.statusbar.show
        self.sidebar.show = self.viewer.config.ui.sidebar.show
        self.sidedock.show = self.viewer.config.ui.sidedock.show
        self.viewer.state.changed.connect(self._on_state_changed)

    @property
    def sidebar(self) -> SideBarRight:
        """SideBarRight: Content sidebar embedded in the main viewport."""
        return self.viewport.sidebar

    @property
    def settings(self) -> ViewerSettings:
        """ViewerSettings: Reusable Viewer-owned settings window."""
        return self._settings

    def init(self) -> None:
        """Size and show the main window, then refresh the sidebar."""
        self.window.resize(self.viewer.config.window.width, self.viewer.config.window.height)
        if self.viewer.config.window.fullscreen:
            self.window.widget.showFullScreen()
        else:
            self.window.widget.show()

        self.sidebar.update()

    def _on_state_changed(self, path: str, value: object) -> None:
        """Synchronize component visibility with global viewer state."""
        components = {
            "ui.menubar.show": self.menubar,
            "ui.toolbar.show": self.toolbar,
            "ui.sidebar.show": self.sidebar,
            "ui.sidedock.show": self.sidedock,
            "ui.statusbar.show": self.statusbar,
        }
        component = components.get(path)
        if component is not None:
            component.show = bool(value)
