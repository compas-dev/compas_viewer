from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGridLayout

if TYPE_CHECKING:
    from .layout import Layout


class ViewportLayout:
    """
    The ViewportLayout class manages all
    the layout and other UI-related information of the main viewport.

    Parameters
    ----------
    layout : :class:`compas_viewer.layout.Layout`
        The parent layout.

    Attributes
    ----------
    layout : :class:`compas_viewer.layout.Layout`
        The parent layout.
    viewer : :class:`compas_viewer.Viewer`
        The parent viewer.
    config : :class:`compas_viewer.configurations.Viewport`
        The window configuration.

    See Also
    --------
    :class:`compas_viewer.configurations.layout_config.ViewportConfig`
    :PySide6:`PySide6/QtWidgets/QGridLayout`
    """

    def __init__(self, layout: "Layout"):
        self.layout = layout
        self.viewer = self.layout.viewer
        self.config = layout.config.viewport

    def init(self):
        """
        Set up the viewport layout.
        """

        #  Viewport layout: this is usually fixed.
        self.viewport_layout = QGridLayout()
        self.viewport_layout.setContentsMargins(1, 1, 1, 1)
        self.layout.window.window_layout.addLayout(self.viewport_layout)

        for k, i in self.config.data.items():
            assert isinstance(i, dict)
            if i["category"] == "render":
                self.viewport_layout.addWidget(self.layout.viewer.renderer, 1, 1)
            else:
                raise NotImplementedError(f"Ttype {i['render']} not implemented.")
