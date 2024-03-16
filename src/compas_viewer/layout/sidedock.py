from typing import TYPE_CHECKING
from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from .propertyform import Propertyform
from .slider import Slider
from .treeform import Treeform

if TYPE_CHECKING:
    from .layout import Layout


class SidedockLayout:
    """
    The SidedockLayout class manages all
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
        self.sidedock.setMinimumWidth(200)
        scroll = QScrollArea()
        self.sidedock.setWidget(scroll)
        content = QWidget()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        self.sidedock_layout = QVBoxLayout(content)
        self.sidedock_layout.addStretch(2)

        self.elements: list[Union[Slider, Treeform, Propertyform]] = []

    def init(self):
        self.sidedock.setLayout(self.sidedock_layout)
        self.viewer.window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.sidedock)

    def add_element(self, element: Union[Slider, Treeform, Propertyform]):
        self.sidedock_layout.insertWidget(self.sidedock_layout.count() - 1, element, element.stretch)
        self.elements.append(element)
        element.viewer = self.viewer

    def update(self):
        for element in self.elements:
            element.update()
