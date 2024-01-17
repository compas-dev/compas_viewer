from typing import TYPE_CHECKING

from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QWidget

from compas_viewer.configurations.layout_config import LayoutConfig

from .menubar import MenubarLayout
from .sidedocks import SidedockLayout
from .statusbar import StatusbarLayout
from .toolbar import ToolbarLayout
from .viewport import ViewportLayout
from .window import WindowLayout

if TYPE_CHECKING:
    from compas_viewer import Viewer


class Layout:
    """
    The Layout class manages all the layout and other UI-related information of the viewer.

    Parameters
    ----------
    config : :class:`compas_viewer.configurations.layout_config.LayoutConfig`
        The configuration object for the layout.

    Attributes
    ----------
    config : :class:`compas_viewer.configurations.layout_config.LayoutConfig`
        The configuration object for the layout.
    viewer : :class:`compas_viewer.viewer.Viewer`
        The parent viewer.
    window : :class:`compas_viewer.layout.layout.WindowLayout`
        The window layout.
    statusbar : :class:`compas_viewer.layout.layout.StatusbarLayout`
        The status bar layout.
    menubar : :class:`compas_viewer.layout.layout.MenubarLayout`
        The menu bar layout.
    viewport : :class:`compas_viewer.layout.layout.ViewportLayout`
        The viewport layout.
    toolbar : :class:`compas_viewer.layout.layout.ToolbarLayout`
        The tool bar layout.
    sidedock : :class:`compas_viewer.layout.layout.SidedockLayout`
        The side dock layout.

    See Also
    --------
    :class:`compas_viewer.configurations.layout_config.LayoutConfig`

    References
    ----------
    :PySide6:`PySide6/QtWidgets/QLayout`
    """

    def __init__(self, viewer: "Viewer", config: LayoutConfig):
        # Basic
        self.viewer = viewer
        self.config = config

        # Widgets
        self.central_widget = QWidget(self.viewer.window)
        self.window = WindowLayout(self)
        self.statusbar = StatusbarLayout(self)
        self.menubar = MenubarLayout(self)
        self.viewport = ViewportLayout(self)
        self.toolbar = ToolbarLayout(self)
        self.sidedock = SidedockLayout(self)

    def init(self):
        """
        Set up the layout.
        """

        # GL
        self._glFormat = QSurfaceFormat()
        self._glFormat.setVersion(2, 1)
        self._glFormat.setProfile(QSurfaceFormat.OpenGLContextProfile.CompatibilityProfile)
        self._glFormat.setDefaultFormat(self._glFormat)
        QSurfaceFormat.setDefaultFormat(self._glFormat)
        # Qt.ApplicationAttribute.AA_ShareOpenGLContexts = self.viewer.render

        # Layout
        self.window.init()
        self.statusbar.init()
        self.menubar.init()
        self.toolbar.init()
        self.sidedock.init()
        self.viewport.init()

        self.viewer.window.setCentralWidget(self.central_widget)

    # TODO
    # def _resize(self, width: int, height: int):
    #     """Resize the main window programmatically.

    #     Parameters
    #     ----------
    #     width: int
    #         Width of the viewer window.
    #     height: int
    #         Height of the viewer window.

    #     """
    #     self._window.resize(width, height)
    #     desktop = self._app.desktop()  # type: ignore
    #     rect = desktop.availableGeometry()
    #     x = int(0.5 * (rect.width() - width))
    #     y = int(0.5 * (rect.height() - height))
    #     self._window.setGeometry(x, y, width, height)
    #     self.config.width = width
    #     self.config.height = height
