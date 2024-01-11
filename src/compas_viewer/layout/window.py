from os import path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .layout import Layout

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QVBoxLayout

from compas_viewer import DATA


class WindowLayout:
    """
    The WindowLayout class manages all
    the layout and other UI-related information of the window itself.

    Parameters
    ----------
    layout : :class:`compas_viewer.layout.Layout`
        The parent layout.

    Attributes
    ----------
    layout : :class:`compas_viewer.layout.Layout`
        The parent layout.
    viewer : :class:`compas_viewer.viewer.Viewer`
        The parent viewer.
    config : :class:`compas_viewer.configurations.WindowConfig`
        The window configuration.

    See Also
    --------
    :class:`compas_viewer.configurations.layout_config.WindowConfig`

    References
    ----------
    :PySide6:`PySide6/Qtdgets/QMainWindow`
    """

    def __init__(self, layout: "Layout"):
        self.layout = layout
        self.viewer = self.layout.viewer
        self.config = layout.config.window

        #  Window layout: this is usually fixed.
        self.window_layout = QVBoxLayout(self.layout.central_widget)
        self.window_layout.setSpacing(0)
        self.window_layout.setContentsMargins(0, 0, 0, 0)

    def init(self):
        """
        Set up the window layout.
        """
        #  Window size
        if self.config.fullscreen:
            self.viewer.window.setWindowState(self.viewer.window.windowState() | Qt.WindowState.WindowMaximized)
        else:
            self.layout.viewer.window.resize(self.config.width, self.config.height)

        #  Window title
        self.viewer.app.setApplicationName(self.config.title)

        #  Window about
        self.about_label = QLabel(self.config.about)

        #  Window icon: fixed
        self.viewer.app.setWindowIcon(QIcon(path.join(DATA, "compas_icon_white.png")))  # type: ignore

    # ==========================================================================
    # Messages
    # ==========================================================================

    def about(self):
        """Display the about message as defined in the config file."""
        QMessageBox.about(self.viewer.window, "About", self.config.about)

    def info(self, message: str):
        """Display info.

        Parameters
        ----------
        message : str
            An info message.
        """
        QMessageBox.information(self.viewer.window, "Info", message)

    def warning(self, message: str):
        """Display a warning.

        Parameters
        ----------
        message : str
            A warning message.
        """
        QMessageBox.warning(self.viewer.window, "Warning", message)

    def critical(self, message: str):
        """Display a critical warning.

        Parameters
        ----------
        message : str
            A critical warning message.
        """
        QMessageBox.critical(self.viewer.window, "Critical", message)

    def question(self, message: str) -> bool:
        """Ask a question.

        Parameters
        ----------
        message : str
            A question.
        """
        flags = QMessageBox.StandardButton.Yes
        flags |= QMessageBox.StandardButton.No
        response = QMessageBox.question(self.viewer.window, "Question", message, flags)  # type: ignore
        if response == QMessageBox.StandardButton.Yes:
            return True
        return False

    def confirm(self, message: str) -> bool:
        """Confirm the execution of an action.

        Parameters
        ----------
        message : str
            Message to inform the user.

        Returns
        -------
        bool
            True if the user confirms.
            False otherwise.
        """
        flags = QMessageBox.StandardButton.Ok
        flags |= QMessageBox.StandardButton.Cancel
        response = QMessageBox.warning(self.viewer.window, "Confirmation", message, flags)
        if response == QMessageBox.StandardButton.Ok:
            return True
        return False
