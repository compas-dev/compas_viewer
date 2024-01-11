from typing import TYPE_CHECKING

from PySide6.QtCore import QDate
from PySide6.QtCore import QDateTime
from PySide6.QtCore import QLocale
from PySide6.QtCore import QMetaObject
from PySide6.QtCore import QObject
from PySide6.QtCore import QPoint
from PySide6.QtCore import QRect
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtCore import QTime
from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction
from PySide6.QtGui import QBrush
from PySide6.QtGui import QColor
from PySide6.QtGui import QConicalGradient
from PySide6.QtGui import QCursor
from PySide6.QtGui import QFont
from PySide6.QtGui import QFontDatabase
from PySide6.QtGui import QGradient
from PySide6.QtGui import QIcon
from PySide6.QtGui import QImage
from PySide6.QtGui import QKeySequence
from PySide6.QtGui import QLinearGradient
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPalette
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QRadialGradient
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtGui import QTransform
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QDockWidget
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLayout
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QMenuBar
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QStatusBar
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas_viewer import DATA
from compas_viewer.configurations.layout_config import LayoutConfig

from .window import WindowLayout
from .statusbar import StatusBarLayout
from .menubar import MenuBarLayout
from . viewport import ViewportLayout

if TYPE_CHECKING:
    from compas_viewer import Viewer

from PySide6.QtWidgets import QMainWindow


class Layout:
    """
    The Layout class manages all the layout and other UI-related information of the viewer.

    It is the master class that invokes the:`compas_viewer.layouts.layout.WindowLayout`, `compas_viewer.layouts.layout.BodyLayout` and others.
    # TODO
    Parameters
    ----------
    config : :class:`compas_viewer.configurations.layout_config.LayoutConfig`
        The configuration object for the layout.

    See Also
    --------
    :class:`compas_viewer.configurations.layout_config.LayoutConfig`
    """

    def __init__(self, viewer: "Viewer", config: LayoutConfig):
        # Basic
        self.viewer = viewer
        self.config = config

        # Widgets
        self.window = WindowLayout(self)
        self.statusbar = StatusBarLayout(self)
        self.menubar = MenuBarLayout(self)
        self.viewport = ViewportLayout(self)



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
        self.viewport.init()


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

