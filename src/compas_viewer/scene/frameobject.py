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
        size: Optional[float] = 1,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.size = size

    def _read_lines_data(self) -> ShaderDataType:
        trans = Transformation.from_frame_to_frame(Frame.worldXY(), self.frame)

        positions = []
        colors = []
        elements = []

        # X direction
        colors.append(Color.red())
        colors.append(Color.red())
        positions.append(Point(0, 0, 0).transformed(trans))
        positions.append(Point(self.size, 0, 0).transformed(trans))
        elements.append([0, 1])

        # Y direction
        colors.append(Color.green())
        colors.append(Color.green())
        positions.append(Point(0, 0, 0).transformed(trans))
        positions.append(Point(0, self.size, 0).transformed(trans))
        elements.append([2, 3])

        # Z direction
        colors.append(Color.blue())
        colors.append(Color.blue())
        positions.append(Point(0, 0, 0).transformed(trans))
        positions.append(Point(0, 0, self.size).transformed(trans))
        elements.append([4, 5])

        return positions, colors, elements

    def _read_points_data(self) -> Optional[ShaderDataType]:
        return None

    def _read_frontfaces_data(self) -> Optional[ShaderDataType]:
        return None

    def _read_backfaces_data(self) -> Optional[ShaderDataType]:
        return None
