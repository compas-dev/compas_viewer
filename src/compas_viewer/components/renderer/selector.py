from typing import TYPE_CHECKING

from numpy import all
from numpy import any
from numpy import array
from numpy import frombuffer
from numpy import uint8
from numpy import unique
from OpenGL import GL
from PySide6.QtCore import QObject
from PySide6.QtCore import QPoint
from PySide6.QtCore import Signal

if TYPE_CHECKING:
    from .renderer import Renderer


class Selector(QObject):
    """Selector class manages all selection operations for the viewer.

    Parameters
    ----------
    renderer : :class:`compas_viewer.components.renderer.Renderer`
        The renderer instance.

    Attributes
    ----------
    renderer : :class:`compas_viewer.components.renderer.Renderer`
        The renderer instance.
    enable_selector : bool
        Enable the selector.
    selectioncolor : :class:`compas.colors.Color`
        The color of the selected items.
    ANTI_ALIASING_FACTOR : int
        The anti-aliasing factor for the drag selection.

    References
    ----------
    * https://doc.qt.io/qtforpython-6/PySide6/QtCore/Signal.html
    """

    # The anti-aliasing factor for the drag selection.
    ANTI_ALIASING_FACTOR = 10

    # Enhance pixel  width for selection.
    PIXEL_SELECTION_INCREMENTAL = 2

    select = Signal()
    deselect = Signal()
    multiselect = Signal()
    drag_selection = Signal()
    drag_deselection = Signal()

    def __init__(
        self,
        renderer: "Renderer",
    ):
        self.enable_selector = renderer.config.selector.enable_selector
        if not self.enable_selector:
            return
        super().__init__()
        self.renderer = renderer
        self.viewer = renderer.viewer
        self.controller = renderer.viewer.controller
        self.selectioncolor = renderer.config.selector.selectioncolor

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
        for _, obj in self.renderer.viewer.instance_colors.items():
            obj.is_selected = False

        x = self.renderer.viewer.controller.mouse.last_pos.x()
        y = self.renderer.viewer.controller.mouse.last_pos.y()
        instance_color = self.read_instance_color((x, y, x, y))
        unique_color = unique(instance_color, axis=0, return_counts=False)

        selected_obj = self.renderer.viewer.instance_colors.get(tuple(unique_color[0]))  # type: ignore
        if selected_obj:
            selected_obj.is_selected = True

    def deselect_action(self):
        """Deselect the object under the mouse cursor."""

        x = self.renderer.viewer.controller.mouse.last_pos.x()
        y = self.renderer.viewer.controller.mouse.last_pos.y()
        instance_color = self.read_instance_color((x, y, x, y))
        unique_color = unique(instance_color, axis=0, return_counts=False)

        selected_obj = self.renderer.viewer.instance_colors.get(tuple(unique_color[0]))  # type: ignore
        if selected_obj:
            selected_obj.is_selected = False

    def multiselect_action(self):
        """Multiselect the object under the mouse cursor. Similar to the select action.

        See Also
        --------
        :func:`compas_viewer.components.renderer.selector.Selector.select_action`
        """
        x = self.renderer.viewer.controller.mouse.last_pos.x()
        y = self.renderer.viewer.controller.mouse.last_pos.y()
        instance_color = self.read_instance_color((x, y, x, y))
        unique_color = unique(instance_color, axis=0, return_counts=False)

        selected_obj = self.renderer.viewer.instance_colors.get(tuple(unique_color[0]))  # type: ignore
        if selected_obj:
            selected_obj.is_selected = True

    def drag_selection_action(self):
        """Drag select the objects in the rectangle area."""

        # Deselect all objects first
        for _, obj in self.renderer.viewer.instance_colors.items():
            obj.is_selected = False

        instance_color = self.read_instance_color(
            (self.drag_start_pt.x(), self.drag_start_pt.y(), self.drag_end_pt.x(), self.drag_end_pt.y())
        )
        unique_colors = unique(instance_color, axis=0, return_counts=True)
        unique_colors = array(
            [unique_colors[0][i] for i, count in enumerate(unique_colors[1]) if count > self.ANTI_ALIASING_FACTOR]
        )

        if len(unique_colors) == 0:
            return

        for color, obj in self.renderer.viewer.instance_colors.items():
            if any(all(color == unique_colors, axis=1)):
                obj.is_selected = True
                continue

    def drag_deselection_action(self):
        """Drag deselect the objects in the rectangle area. Similar to the drag selection action.

        See Also
        --------
        :func:`compas_viewer.components.renderer.selector.Selector.drag_selection_action`
        """

        instance_color = self.read_instance_color(
            (self.drag_start_pt.x(), self.drag_start_pt.y(), self.drag_end_pt.x(), self.drag_end_pt.y())
        )
        unique_colors = unique(instance_color, axis=0, return_counts=True)
        unique_colors = array(
            [unique_colors[0][i] for i, count in enumerate(unique_colors[1]) if count > self.ANTI_ALIASING_FACTOR]
        )

        if len(unique_colors) == 0:
            return

        for color, obj in self.renderer.viewer.instance_colors.items():
            if any(all(color == unique_colors, axis=1)):
                obj.is_selected = False
                continue

    def read_instance_color(self, box: tuple[int, int, int, int]):
        """
        Paint the instance map quickly, and then read the color of the specified area.

        Parameters
        ----------
        box : tuple[int, int, int, int]
            The box area [x1, y1, x2, y2] to be read. x1=x2 and y1=y2 means a single point.

        Notes
        -----
        The instance map is used by the selector to identify selected objects.
        The mechanism of a :class:`compas_viewer.components.renderer.selector.Selector`
        is picking the color from instance map and then find the corresponding object.
        Anti aliasing, which is always force opened in many machines,  can cause color picking inaccuracy.

        The instance buffer created by the GL is based on the "device-independent pixels",
        while "physical pixels" is the common unit. The method :func:`PySide6.QtGui.QPaintDevice.devicePixelRatio()`
        plays a role in the conversion between the two units, which is different on different devices.
        For example, Mac Retina display has a devicePixelRatio of 2.0.
        This method contains an uniform-sampling-similar math operation,
        which is not absolutely accurate but enough for the selection.

        See Also
        --------
        :func:`compas_viewer.components.renderer.selector.Selector.ANTI_ALIASING_FACTOR`
        :attr:`compas_viewer.components.renderer.rendermode`

        References
        ----------
        * https://doc.qt.io/qt-6/qscreen.html#devicePixelRatio-prop
        * https://registry.khronos.org/OpenGL-Refpages/gl4/html/glReadPixels.xhtml
        * https://doc.qt.io/qt-6/qopenglwidget.html#makeCurrent
        """

        # 0. Get the rectangle area.
        x1, y1, x2, y2 = box
        x, y = min(x1, x2), self.viewer.layout.config.window.height - max(y1, y2)
        width = max(self.PIXEL_SELECTION_INCREMENTAL, abs(x1 - x2))
        height = max(self.PIXEL_SELECTION_INCREMENTAL, abs(y1 - y2))
        r = self.renderer.devicePixelRatio()

        # 1. Repaint the canvas with instance color.
        self.renderer.makeCurrent()
        self.renderer.paintGL(is_instance=True)

        # 2. Read the instance buffer.
        instance_buffer = GL.glReadPixels(x * r, y * r, width * r, height * r, GL.GL_RGB, GL.GL_UNSIGNED_BYTE)

        # 3. Return the instance color.
        #      From 1-3, the canvas goes through a quick repaint process, which should be not noticeable to the user.
        instance_map = frombuffer(buffer=instance_buffer, dtype=uint8).reshape(-1, 3)

        return instance_map
