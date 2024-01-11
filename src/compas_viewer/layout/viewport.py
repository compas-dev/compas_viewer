from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .layout import Layout


class ViewportLayout(Layout):
        """
    The ViewportLayout class manages all
    the layout and other UI-related information of the main viewport.

    Parameters
    ----------
    layout : :class:`compas_viewer.layouts.Layout`
        The parent layout.

    Attributes
    ----------
    layout : :class:`compas_viewer.layouts.Layout`
        The parent layout.
    viewer : :class:`compas_viewer.Viewer`
        The parent viewer.
    config : :class:`compas_viewer.configurations.WindowConfig`
        The window configuration.
    """

    def __init__(self, layout: "Layout"):
        self.layout = layout
        self.viewer = self.layout.viewer
        self.config = layout.config.window

    def init(self):
        """
        Set up the window layout.
    def init(self):
        self.layout.body_layout.addWidget(self.layout.viewer.render)
        self.layout.window.setCentralWidget(self.layout.viewer.render)
