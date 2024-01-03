from math import ceil
from typing import TYPE_CHECKING

from numpy import array
from numpy import frombuffer
from numpy import uint8
from numpy import unique
from numpy.typing import NDArray
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

    # The anti-aliasing factor for the drag selection.
    ANTI_ALIASING_FACTOR = 10

    select = Signal()
    deselect = Signal()
    multiselect = Signal()
    drag_selection = Signal()
    drag_deselection = Signal()

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
        self.drag_end_pt: QPoint

        self.select.connect(self.select_action)
        self.deselect.connect(self.deselect_action)
        self.multiselect.connect(self.multiselect_action)
        self.drag_selection.connect(self.drag_selection_action)
        self.drag_deselection.connect(self.drag_deselection_action)

    def select_action(self):
        """Select the object under the mouse cursor."""

        # Deselect all objects first
        for _, obj in self.render.viewer.instance_colors.items():
            obj.is_selected = False

        x = self.controller.mouse.last_pos.x()
        y = self.controller.mouse.last_pos.y()
        instance_color = tuple(self.read_instance_map()[y][x])

        selected_obj = self.render.viewer.instance_colors.get(instance_color)  # type: ignore
        if selected_obj:
            selected_obj.is_selected = True

    def deselect_action(self):
        """Deselect the object under the mouse cursor."""
        x = self.controller.mouse.last_pos.x()
        y = self.controller.mouse.last_pos.y()
        instance_color = tuple(self.read_instance_map()[y][x])

        selected_obj = self.render.viewer.instance_colors.get(instance_color)  # type: ignore
        if selected_obj:
            selected_obj.is_selected = False

    def multiselect_action(self):
        """Multiselect the object under the mouse cursor. Similar to the select action.

        See Also
        --------
        :func:`compas_viewer.components.render.selector.Selector.select_action`
        """

        x = self.controller.mouse.last_pos.x()
        y = self.controller.mouse.last_pos.y()
        instance_color = tuple(self.read_instance_map()[y][x])

        selected_obj = self.render.viewer.instance_colors.get(instance_color)  # type: ignore
        if selected_obj:
            selected_obj.is_selected = not selected_obj.is_selected

    def drag_selection_action(self):
        """Drag select the objects in the rectangle area."""

        # Deselect all objects first
        for _, obj in self.render.viewer.instance_colors.items():
            obj.is_selected = False

        instance_map = self.read_instance_map()
        box_map = instance_map[
            self.drag_start_pt.y() : self.drag_end_pt.y(),  # noqa: E203
            self.drag_start_pt.x() : self.drag_end_pt.x(),  # noqa: E203
        ]

        unique_colors = unique(box_map.reshape(box_map.shape[0] * box_map.shape[1], 3), axis=0, return_counts=True)
        unique_colors = array(
            [unique_colors[0][i] for i, count in enumerate(unique_colors[1]) if count > self.ANTI_ALIASING_FACTOR]
        )

        for color, obj in self.render.viewer.instance_colors.items():
            if color in unique_colors:
                obj.is_selected = True
                continue

    def drag_deselection_action(self):
        """Drag deselect the objects in the rectangle area. Similar to the drag selection action.

        See Also
        --------
        :func:`compas_viewer.components.render.selector.Selector.drag_selection_action`
        """

        instance_map = self.read_instance_map()
        box_map = instance_map[
            self.drag_start_pt.y() : self.drag_end_pt.y(),  # noqa: E203
            self.drag_start_pt.x() : self.drag_end_pt.x(),  # noqa: E203
        ]

        unique_colors = unique(box_map.reshape(box_map.shape[0] * box_map.shape[1], 3), axis=0, return_counts=True)
        unique_colors = array(
            [unique_colors[0][i] for i, count in enumerate(unique_colors[1]) if count > self.ANTI_ALIASING_FACTOR]
        )

        for color, obj in self.render.viewer.instance_colors.items():
            if color in unique_colors:
                obj.is_selected = False
                continue

    def read_instance_map(self) -> NDArray:
        """Compile the instance buffer into instance map.

        Returns
        -------
        instance_color : NDArray
            The instance map.

        Notes
        -----
        The instance buffer created by the GL is based on the "device-independent pixels",
        while "physical pixels" is the common unit. The method :func:`PySide6.QtGui.QPaintDevice.devicePixelRatio()`
        plays a role in the conversion between the two units, which is different on different devices.
        For example, Mac Retina display has a devicePixelRatio of 2.0.
        This method contains an uniform-sampling-similar math operation,
        which is not absolutely accurate but enough for the selection.

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
        return instance_map
