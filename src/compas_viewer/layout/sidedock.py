from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget

if TYPE_CHECKING:
    from .layout import Layout


class SideDockLayout:
    """
    The SideDockLayout class manages all
    the layout and other UI-related information of the side dock itself.

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
    :class:`compas_viewer.configurations.layout_config.SidedockConfig`

    References
    ----------
    :PySide6:`PySide6/QtWidgets/QDockWidget`
    """

    def __init__(self, layout: "Layout"):
        self.layout = layout
        self.viewer = self.layout.viewer
        self.config = layout.config.window
        self.config = layout.config.toolbar
        self.sidedock = QDockWidget()

    def init(self):
        self.viewer.window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.sidedock)
