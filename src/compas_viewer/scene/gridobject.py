from typing import Any
from typing import Optional

from compas.colors import Color
from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Transformation
from compas.itertools import flatten
from compas_viewer.base import Base
from compas_viewer.gl import make_index_buffer
from compas_viewer.gl import make_vertex_buffer
from compas_viewer.renderer.shaders import Shader

from .sceneobject import ShaderDataType


class GridObject(Base):
    """
    The scene object of the world XY grid. It is a subclass of the FrameObject.

    Parameters
    ----------
    frame : :class:`compas.geometry.Frame`
        The transformation frame. The default is the world XY frame.
    framesize : tuple[float, int, float, int]
        The size of the grid in [dx, nx, dy, ny] format.
        Notice that the `nx` and `ny` must be even numbers.
    gridmode : str
        The mode of the grid. Options are "full" and "quadrant".
    linecolor : :class:`compas.colors.Color`
        The color of the grid lines.
    show_framez : bool
        If True, the Z axis of the grid will be shown.

    Attributes
    ----------
    frame : :class:`compas.geometry.Frame`
        The transformation frame.
    gridmode : str
        The mode of the grid. Options are "full" and "quadrant".
    linecolor : :class:`compas.colors.Color`
        The color of the grid lines.
    dx : float
        The size of the grid in the X direction.
    nx : int
        The number of grid cells in the X direction.
    dy : float
        The size of the grid in the Y direction.
    ny : int
        The number of grid cells in the Y direction.
    show_framez : bool
        If the Z axis of the grid is shown.

    Notes
    -----
    The world grid object is always unselectable.

    See Also
    --------
    :class:`compas_viewer.scene.FrameObject`
    :class:`compas.geometry.Frame`
    """

    def __init__(
        self,
        frame: Frame = Frame.worldXY(),
        framesize: Optional[tuple[float, int, float, int]] = None,
        gridmode: Optional[str] = "full",
        linecolor: Optional[Color] = None,
        show_framez: Optional[bool] = None,
        **kwargs,
    ):
        self.frame = frame
        self.linecolor = linecolor if linecolor else self.viewer.config.renderer.gridcolor
        self.gridmode = gridmode
        self.dx = framesize[0] if framesize else 10.0
        self.nx = framesize[1] if framesize else 10
        self.dy = framesize[2] if framesize else 10.0
        self.ny = framesize[3] if framesize else 10
        self.show_framez = show_framez if show_framez else False
        if self.nx % 2 != 0 or self.ny % 2 != 0:
            raise ValueError("The number of grid cells in the X and Y directions must be even numbers.")
        self.show_lines = True
        self._matrix_buffer = None
        self._lines_data = None

    def _read_lines_data(self) -> ShaderDataType:
        trans = Transformation.from_frame_to_frame(Frame.worldXY(), self.frame)

        positions = []
        colors = []
        elements = []

        # Determine grid mode settings
        if self.gridmode == "full":
            x_positions = [-self.dx + self.dx / self.nx * i for i in range(self.nx * 2 + 1)]
            y_positions = [-self.dy + self.dy / self.ny * i for i in range(self.ny * 2 + 1)]
            x_bound = (-self.dx, self.dx)
            y_bound = (-self.dy, self.dy)
            base_index = (self.nx * 2 + 1) * 4
        elif self.gridmode == "quadrant":
            x_positions = [self.dx / self.nx * i for i in range(self.nx + 1)]
            y_positions = [self.dy / self.ny * i for i in range(self.ny + 1)]
            x_bound = (0, self.dx)
            y_bound = (0, self.dy)
            base_index = (self.nx + 1) * 4

        # X direction
        for i, x in enumerate(x_positions):
            # Color Y axis positive green if x == 0.
            if x == 0:
                colors.extend([self.linecolor, self.linecolor, Color.green(), Color.green()])
            else:
                colors.extend([self.linecolor] * 4)

            p1 = Point(x, y_bound[0], 0).transformed(trans)
            p2 = Point(x, 0, 0).transformed(trans)
            p3 = Point(x, y_bound[1], 0).transformed(trans)
            positions.extend([p1, p2, p2, p3])

            elements.append([i * 4 + j for j in range(4)])

        # Y direction
        for i, y in enumerate(y_positions):
            # Color X axis positive red if y == 0.
            if y == 0:
                colors.extend([self.linecolor, self.linecolor, Color.red(), Color.red()])
            else:
                colors.extend([self.linecolor] * 4)

            p1 = Point(x_bound[0], y, 0).transformed(trans)
            p2 = Point(0, y, 0).transformed(trans)
            p3 = Point(x_bound[1], y, 0).transformed(trans)
            positions.extend([p1, p2, p2, p3])

            elements.append([base_index + i * 4 + j for j in range(4)])

        # Z direction
        if self.show_framez:
            colors.extend([Color.blue(), Color.blue()])
            p1 = Point(0, 0, 0).transformed(trans)
            p2 = Point(0, 0, self.dx / 2).transformed(trans)
            positions.extend([p1, p2])
            elements.append([base_index + len(y_positions) * 4, base_index + len(y_positions) * 4 + 1])

        return positions, colors, elements

    def init(self):
        """Initialize the object"""
        self._lines_data = self._read_lines_data()
        self.make_buffers()

    def make_buffers(self):
        """Create all buffers from object's data"""
        if self._lines_data is not None:
            data = self._lines_data
            self._lines_buffer = self.make_buffer_from_data(data)

    def make_buffer_from_data(self, data: ShaderDataType) -> dict[str, Any]:
        """Create buffers from point/line/face data.

        Parameters
        ----------
        data : tuple[list[:class:`compas.geometry.Point`], list[:class:`compas.colors.Color`], list[int]]
            Contains positions, colors, elements for the buffer.

        Returns
        -------
        buffer_dict : dict[str, Any]
            A dict with created buffer indexes.
        """
        positions, colors, elements = data
        flat_positions = list(flatten(positions))
        flat_colors = list(flatten([color.rgba for color in colors]))
        flat_elements = list(flatten(elements))
        return {
            "positions": make_vertex_buffer(flat_positions),
            "colors": make_vertex_buffer(flat_colors),
            "elements": make_index_buffer(flat_elements),
            "n": len(flat_elements),
        }

    def draw(self, shader: Shader):
        shader.enable_attribute("position")
        shader.enable_attribute("color")
        shader.bind_attribute("position", self._lines_buffer["positions"])
        shader.bind_attribute("color", self._lines_buffer["colors"], step=4)
        shader.draw_lines(elements=self._lines_buffer["elements"], n=self._lines_buffer["n"], width=1, background=True)
        shader.disable_attribute("position")
        shader.disable_attribute("color")
