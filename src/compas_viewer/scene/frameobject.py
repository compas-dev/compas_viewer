from typing import Optional

from compas.colors import Color
from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Transformation

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject


class FrameObject(ViewerSceneObject):
    """
    The scene object of the COMPAS Frame.
    With its modifiable cell size and dimension.

    Parameters
    ----------
    frame : :class:`compas.geometry.Frame`
        The frame geometry.
    framesize : tuple[float, int, float, int]
        The size of the grid in [dx, nx, dy, ny] format.
        Notice that the `nx` and `ny` must be even numbers.
    linecolor : :class:`compas.colors.Color`
        The color of the grid lines.
    show_framez : bool
        If True, the Z axis of the grid will be shown.

    Attributes
    ----------
    frame : :class:`compas.geometry.Frame`
        The frame geometry.
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

    See Also
    --------
    :class:`compas.geometry.Frame`
    """

    def __init__(
        self,
        frame: Frame,
        framesize: Optional[tuple[float, int, float, int]] = None,
        linecolor: Optional[Color] = None,
        show_framez: Optional[bool] = None,
        **kwargs
    ):
        super().__init__(item=frame, **kwargs)
        self.frame = frame
        self.linecolor = linecolor or self.viewer.config.linecolor
        self.dx = framesize[0] if framesize else self.viewer.config.framesize[0]
        self.nx = framesize[1] if framesize else self.viewer.config.framesize[1]
        self.dy = framesize[2] if framesize else self.viewer.config.framesize[2]
        self.ny = framesize[3] if framesize else self.viewer.config.framesize[3]
        self.show_framez = show_framez or self.viewer.config.show_framez
        if self.nx % 2 != 0 or self.ny % 2 != 0:
            raise ValueError("The number of grid cells in the X and Y directions must be even numbers.")
        self.show_lines = True

    def _read_lines_data(self) -> ShaderDataType:
        trans = Transformation.from_frame_to_frame(Frame.worldXY(), self.frame)

        positions = []
        colors = []
        elements = []
        i = 0

        # X direction
        for i in range(self.nx + 1):
            x = -self.dx / 2 + self.dx / self.nx * i
            # Color Y axis positive green.
            if x == 0:
                colors.extend([self.linecolor, self.linecolor, Color.green(), Color.green()])
            else:
                colors.extend([self.linecolor] * 4)
            positions.extend(
                [
                    Point(x, -self.dy / 2, 0).transformed(trans),
                    Point(x, 0, 0).transformed(trans),
                    Point(x, 0, 0).transformed(trans),
                    Point(x, self.dy / 2, 0).transformed(trans),
                ]
            )
            elements.append([i * 4, i * 4 + 1, i * 4 + 2, i * 4 + 3])

        # Y direction
        for i in range(self.ny + 1):
            y = -self.dy / 2 + self.dy / self.ny * i
            # Color X axis positive red.
            if y == 0:
                colors.extend([self.linecolor, self.linecolor, Color.red(), Color.red()])
            else:
                colors.extend([self.linecolor] * 4)
            positions.extend(
                [
                    Point(-self.dx / 2, y, 0).transformed(trans),
                    Point(0, y, 0).transformed(trans),
                    Point(0, y, 0).transformed(trans),
                    Point(self.dx / 2, y, 0).transformed(trans),
                ]
            )
            elements.append(
                [
                    (self.nx + 1) * 4 + i * 4,
                    (self.nx + 1) * 4 + i * 4 + 1,
                    (self.nx + 1) * 4 + i * 4 + 2,
                    (self.nx + 1) * 4 + i * 4 + 3,
                ]
            )

        # Z direction
        if self.show_framez:
            colors.append(Color.blue())
            colors.append(Color.blue())
            positions.append(Point(0, 0, 0).transformed(trans))
            positions.append(Point(0, 0, self.dx / 2).transformed(trans))
            elements.append([(self.nx + 1) * 4 + (self.ny + 1) * 4, (self.nx + 1) * 4 + (self.ny + 1) * 4 + 1])

        return positions, colors, elements

    def _read_points_data(self) -> Optional[ShaderDataType]:
        """Read points data from the object."""
        return None

    def _read_frontfaces_data(self) -> Optional[ShaderDataType]:
        """Read frontfaces data from the object."""
        return None

    def _read_backfaces_data(self) -> Optional[ShaderDataType]:
        """Read backfaces data from the object."""
        return None
