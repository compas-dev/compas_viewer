import numpy as np
from typing import TYPE_CHECKING
import matplotlib.pyplot as plt
from PySide6.QtCore import QObject
from PySide6.QtCore import Signal

if TYPE_CHECKING:
    from .render import Render


class Selector(QObject):
    """Selector class manages all selection operations for the viewer.

    Parameters
    ----------
    render : :class:`compas_viewer.components.render.Render`
        The render instance.

    Attributes
    ----------
    render : :class:`compas_viewer.components.render.Render`
        The render instance.
    enable_selector : bool
        Enable the selector.
    selectioncolor : :class:`compas.colors.Color`
        The color of the selected items.

    References
    ----------
    * https://doc.qt.io/qtforpython-6/PySide6/QtCore/Signal.html
    """

    single_selection = Signal()
    multi_selection = Signal()
    box_selection = Signal()

    def __init__(
        self,
        render: "Render",
    ):
        super().__init__()
        self.render = render
        self.controller = render.viewer.controller
        self.enable_selector = render.config.selector.enable_selector
        self.selectioncolor = render.config.selector.selectioncolor

        self.single_selection.connect(self.single_selection_action)

    def single_selection_action(self):
        x = self.controller.mouse.last_pos.x()
        y = self.controller.mouse.last_pos.y()

        instance_color = self.render.instance_map[y][x]
        print(x, y)

        print(instance_color)

