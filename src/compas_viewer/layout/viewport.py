from typing import TYPE_CHECKING
from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter

if TYPE_CHECKING:
    from compas_viewer.components import Renderer

    from .layout import Layout
    from .treeform import Treeform


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
    viewer : :class:`compas_viewer.viewer.Viewer`
        The parent viewer.
    config : :class:`compas_viewer.configurations.Viewport`
        The window configuration.

    See Also
    --------
    :class:`compas_viewer.configurations.layout_config.ViewportConfig`

    References
    ----------
    :PySide6:`PySide6/QtWidgets/QSplitter`
    """

    def __init__(self, layout: "Layout"):
        self.layout = layout
        self.viewer = self.layout.viewer
        self.config = layout.config.viewport

        self.viewport_layout = QSplitter()
        self.viewport_layout.setContentsMargins(1, 1, 1, 1)

    def init(self):
        """
        Set up the viewport layout.
        """
        #  Viewport layout: this is usually fixed.
        self.layout.window.window_layout.addWidget(self.viewport_layout)

        for k, i in self.config.config.items():
            if i["category"] == "render":
                self.add_element(self.layout.viewer.renderer)
            else:
                raise NotImplementedError(f"Type {i['render']} not implemented.")

    def add_element(self, element: Union["Renderer", "Treeform"], is_horizontal: bool = True):
        """
        Add an element to the viewport layout.

        Parameters
        ----------
        element : Union[:class:`compas_viewer.components.Renderer`, :class:`compas_viewer.layout.Treeform`]
            The element to add to the viewport layout.
        is_horizontal : bool, optional
            Whether to add the element horizontally or vertically. Defaults to True.

        References
        ----------
        :PySide6:`PySide6/QtWidgets/QSplitter`
        """
        if is_horizontal:
            splitter = QSplitter()
            splitter.setOrientation(Qt.Orientation.Vertical)
            splitter.addWidget(element)
            self.viewport_layout.addWidget(splitter)
            self.viewport_layout.setSizes([1000] * self.viewport_layout.count())
        else:
            splitters: list[QSplitter] = [
                self.viewport_layout.widget(i) for i in range(self.viewport_layout.count())
            ]  # type: ignore
            min_splitter = min(splitters, key=lambda splitter: splitter.count())
            min_splitter.addWidget(element)
            min_splitter.setSizes([1000] * min_splitter.count())
