from functools import partial
from os import path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .layout import Layout

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QWidget

from compas_viewer import HERE
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
        self.config = layout.config.toolbar
        self.toolbar = QTabWidget(self.viewer.window)

    def init(self):
        """
        Set up the toolbar layout.
        """

        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.toolbar.sizePolicy().hasHeightForWidth())

        self.toolbar.setSizePolicy(size_policy)
        self.toolbar.setMaximumSize(QSize(16777215, 64))
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        defaulticon = QIcon(path.join(HERE, "icons/compas_icon_white.png"))

        button_size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        for k, i in self.config.config.items():
            parent = QHBoxLayout()

            assert isinstance(i, dict)

            for name, item in i.items():
                action_config = ActionConfig("no")  # type: ignore
                iconpath = path.join(HERE, "icons", f"{name}.svg")
                icon = QIcon(iconpath) if path.exists(iconpath) else defaulticon
                button = QPushButton()
                button.setToolTip(name)
                button.setIcon(icon)
                button.setMinimumSize(QSize(32, 32))
                button.setMaximumSize(QSize(32, 32))

                # button.setFlat(True)
                button.clicked.connect(
                    partial(
                        Action(item["action"], self.viewer, action_config).pressed_action,
                        **item.get("kwargs", {}),
                    )
                )
                button.setSizePolicy(button_size_policy)
                parent.addWidget(button)

            parent.addStretch()
            widget = QWidget()

            widget.setLayout(parent)

            self.toolbar.addTab(widget, k)

        self.layout.window.window_layout.addWidget(self.toolbar)
