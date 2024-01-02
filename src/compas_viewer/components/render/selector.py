from math import ceil
from typing import TYPE_CHECKING

from compas.colors import Color
from numpy import frombuffer
from numpy import uint8
from PySide6.QtCore import QObject
from PySide6.QtCore import QPoint
from PySide6.QtCore import Signal
from scipy.ndimage import zoom

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
    deselect = Signal()
    multi_selection = Signal()
    box_selection = Signal()

    def __init__(
        self,
        render: "Render",
    ):
        self.enable_selector = render.config.selector.enable_selector
        if not self.enable_selector:
            return
        super().__init__()
        self.render = render
        self.viewer = render.viewer
        self.controller = render.viewer.controller
        self.selectioncolor = render.config.selector.selectioncolor

        #  Drag selection
        self.on_drag_selection: bool = False
        self.drag_start_pt: QPoint

        self.single_selection.connect(self.single_selection_action)
        self.deselect.connect(self.deselect_action)

    def single_selection_action(self):
        """Select the object under the mouse cursor."""

        # Deselect all objects first
        for _, obj in self.render.viewer.instance_colors.items():
            obj.is_selected = False

        x = self.controller.mouse.last_pos.x()
        y = self.controller.mouse.last_pos.y()
        instance_color = self.read_instance_map(x, y)

        selected_obj = self.render.viewer.instance_colors.get(instance_color.rgb)
        if selected_obj:
            selected_obj.is_selected = True

    def deselect_action(self):
        """Deselect the object under the mouse cursor."""
        x = self.controller.mouse.last_pos.x()
        y = self.controller.mouse.last_pos.y()
        instance_color = self.read_instance_map(x, y)

        selected_obj = self.render.viewer.instance_colors.get(instance_color.rgb)
        if selected_obj:
            selected_obj.is_selected = False

    def read_instance_map(self, x: int, y: int):
        """Compile the instance buffer into instance map.

        Parameters
        ----------
        x : int
            The x coordinate of the mouse cursor.
        y : int
            The y coordinate of the mouse cursor.

        Returns
        -------
        instance_color : :class:`compas.colors.Color`
            The color in the cursor position of the instance map.

        Notes
        -----
        The instance buffer created by the GL is based on the "device-independent pixels",
        while "physical pixels" is the common unit. The method :meth:`PySide6.QtGui.QPaintDevice.devicePixelRatio()`
        plays a role in the conversion between the two units, which is different on different devices.
        For example, Mac Retina display has a devicePixelRatio of 2.0.
        This method contains an uniform-sampling-similar math operation, which is not absolutely accurate but enough for the selection.

        References
        ----------
        * https://doc.qt.io/qt-6/qscreen.html#devicePixelRatio-prop
        """
        r = self.render.devicePixelRatio()
        x_ratio = self.viewer.config.width / ceil(r * self.viewer.config.width)
        y_ratio = self.viewer.config.height / ceil(r * self.viewer.config.height)
        instance_map = frombuffer(buffer=self.render.instance_buffer, dtype=uint8).reshape(
            ceil(r * self.viewer.config.height), ceil(r * self.viewer.config.width), 3
        )
        instance_map = zoom(instance_map, (x_ratio, y_ratio, 1), order=1)
        instance_map = instance_map[::-1, ::1, :]
        return Color.from_rgb255(*instance_map[y][x])
