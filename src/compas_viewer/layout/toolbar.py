from functools import partial
from os import path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .layout import Layout

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QWidget

from compas_viewer import DATA
from compas_viewer.actions import Action
from compas_viewer.configurations import ActionConfig


class ToolbarLayout:
    """
    The ToolbarLayout class manages all
    the layout and other UI-related information of the toolbar itself.

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
    :class:`compas_viewer.configurations.layout_config.ToolbarConfig`

    References
    ----------
    :PySide6:`PySide6/QtWidgets/QTabWidget`
    """

    def __init__(self, layout: "Layout"):
        self.layout = layout
        self.viewer = self.layout.viewer
        self.config = layout.config.window
        self.config = layout.config.toolbar
        self.toolbar = QTabWidget(self.viewer.window)

    def init(self):
        """
        Set up the toolbar layout.
        """

        _size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        _size_policy.setHorizontalStretch(0)
        _size_policy.setVerticalStretch(0)
        _size_policy.setHeightForWidth(self.toolbar.sizePolicy().hasHeightForWidth())

        self.toolbar.setSizePolicy(_size_policy)
        self.toolbar.setMaximumSize(QSize(16777215, 50))
        _ = QIcon(path.join(DATA, "compas_icon_white.png"))

        for k, i in self.config.data.items():
            parent = QWidget()
            assert isinstance(i, dict)
            for _k, _i in i.items():
                action_config = ActionConfig({"key": "no"})  # type: ignore
                parent.addAction(
                    _k,
                    partial(
                        Action(_i["action"], self.viewer, action_config).pressed_action,
                        **_i.get("kwargs", {}),
                    ),
                )
            self.toolbar.addTab(parent, k)

        self.layout.window.window_layout.addWidget(self.toolbar)
