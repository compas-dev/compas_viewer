import sys
from abc import abstractmethod
from os import path
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
from .menu import Menu

from compas_viewer import DATA
from compas_viewer.configurations.layout_config import LayoutConfig

if TYPE_CHECKING:
    from compas_viewer import Viewer

from PySide6.QtWidgets import QMainWindow


class Layout:
    """
    The :class:`compas_viewer.layouts.Layout` class manages all the layout and other UI-related information of the viewer.

    This is the abstract class for all the layout classes.

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
        self.window = viewer.window
        self.config = config

        # Primitive
        self.window_layout = self.window.layout()

        self.body_layout: QLayout
        self.menubar = self.window.menuBar()
        self.statusbar: QStatusBar = self.window.statusBar()

        # Window

    # def init(self):
    #     """This layout method inside the :class:`compas_viewer.layouts.Layout` class manages the abstract layout logic,
    #     grid layout, vertical layout and horizontal layout, etc. to arrange the widgets in the viewer window.
    #     """

    #     self.window.resize(self.config.width, self.config.height)

    #     #  Window
    #     self.window_layout = QVBoxLayout()
    #     self.window_layout.setSpacing(0)
    #     self.window_layout.setContentsMargins(0, 0, 0, 0)

    #     #  Body
    #     self.body_layout = QGridLayout()
    #     self.body_layout.setContentsMargins(1, 1, 1, 1)
    #     self.window_layout.addLayout(self.body_layout)



        # GL
        # self._glFormat = QSurfaceFormat()
        # self._glFormat.setVersion(2, 1)
        # self._glFormat.setProfile(QSurfaceFormat.OpenGLContextProfile.CompatibilityProfile)
        # self._glFormat.setDefaultFormat(self._glFormat)
        # QSurfaceFormat.setDefaultFormat(self._glFormat)
        # Qt.ApplicationAttribute.AA_ShareOpenGLContexts = self.viewer.render

        # #
        # self._app = QCoreApplication.instance() or QApplication(sys.argv)

        # self._app.references = set()  # type: ignore
        #
        # self._icon = QIcon(path.join(DATA, "compas_icon_white.png"))
        # self._app.setWindowIcon(self._icon)  # type: ignore
        # self._app.setApplicationName(self.viewer.config.title)

    # self._window.setCentralWidget()
    # self._window.setContentsMargins(0, 0, 0, 0)
    # self._app.references.add(self._window)  # type: ignore
    # self._window.resize(self.config.width, self.config.height)

    # if self.viewer.config.fullscreen:
    #     self._window.setWindowState(self._window.windowState() | QtCore.Qt.WindowState.WindowMaximized)

    #     self._init_statusbar()

    # def _init_statusbar(self):
    #     self.statusbar = self._window.statusBar()
    #     self.statusbar.setContentsMargins(0, 0, 0, 0)
    #     self.statusText = QtWidgets.QLabel(self.config.statusbar)
    #     self.statusbar.addWidget(self.statusText, 1)
    #     if self.config.show_fps:
    #         self.statusFps = QtWidgets.QLabel("fps: ")
    #         self.statusbar.addWidget

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

    # # ==========================================================================
    # # Messages
    # # ==========================================================================

    # def about(self):
    #     """Display the about message as defined in the config file."""
    #     QtWidgets.QMessageBox.about(self._window, "About", self.config.about)

    # def info(self, message: str):
    #     """Display info.

    #     Parameters
    #     ----------
    #     message : str
    #         An info message.

    #     """
    #     QtWidgets.QMessageBox.information(self._window, "Info", message)

    # def warning(self, message: str):
    #     """Display a warning.

    #     Parameters
    #     ----------
    #     message : str
    #         A warning message.

    #     """
    #     QtWidgets.QMessageBox.warning(self._window, "Warning", message)

    # def critical(self, message: str):
    #     """Display a critical warning.

    #     Parameters
    #     ----------
    #     message : str
    #         A critical warning message.

    #     """
    #     QtWidgets.QMessageBox.critical(self._window, "Critical", message)

    # def question(self, message: str) -> bool:
    #     """Ask a question.

    #     Parameters
    #     ----------
    #     message : str
    #         A question.

    #     """
    #     flags = QtWidgets.QMessageBox.StandardButton.Yes
    #     flags |= QtWidgets.QMessageBox.StandardButton.No
    #     response = QtWidgets.QMessageBox.question(self._window, "Question", message, flags)  # type: ignore
    #     if response == QtWidgets.QMessageBox.StandardButton.Yes:
    #         return True
    #     return False

    # def confirm(self, message: str) -> bool:
    #     """Confirm the execution of an action.

    #     Parameters
    #     ----------
    #     message : str
    #         Message to inform the user.

    #     Returns
    #     -------
    #     bool
    #         True if the user confirms.
    #         False otherwise.

    #     Examples
    #     --------
    #     .. code-block:: python

    #         if viewer.confirm("Should i continue?"):
    #             continue

    #     """
    #     flags = QtWidgets.QMessageBox.StandardButton.Ok
    #     flags |= QtWidgets.QMessageBox.StandardButton.Cancel
    #     response = QtWidgets.QMessageBox.warning(self._window, "Confirmation", message, flags)
    #     if response == QtWidgets.QMessageBox.StandardButton.Ok:
    #         return True
    #     return False

    # def status(self, message: str):
    #     """Display a message in the status bar.

    #     Parameters
    #     ----------
    #     message : str
    #         A status message.

    #     """
    #     self.statusText.setText(message)

    def fps(self, fps: int):
        """Update fps info in the status bar.

        Parameters
        ----------
        fps : int
            The number of frames per second.

        """
        self._fps.setText(f"fps: {fps}")
