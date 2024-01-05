from typing import List
from typing import Optional
from typing import Tuple

from compas.colors import Color
from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Transformation

from .gridobject import Grid
from .gridobject import GridObject


class FrameObject(GridObject):
    """
    The scene object of the :class:`compas_viewer.geometry.Frame` geometry.
    This scene object is a subclass of :class:`compas_viewer.scene.gridobject.GridObject`.

    Parameters
    ----------
    frame : :class:`compas.geometry.Frame`
        The frame geometry.
    framesize : float
        The size of the frame.
        Default is 1.

    Attributes
    ----------
    frame : :class:`compas.geometry.Frame`
        The frame geometry.
    framesize : float
        The size of the frame.
    FRAME_CELLS : int
        The number of cells in the grid, refer
        to :attr:`compas_viewer.scene.gridobject.Grid.nx` and :attr:`compas_viewer.scene.gridobject.Grid.ny`.
        Default is 10.
    AXIS_COLOR_INDICES : List[List[int]]
        Under this FRAME_CELLS, the color indices for the axes.

    """

    FRAME_CELLS: int = 10
    AXIS_COLOR_INDICES: List[List[int]] = [[115, 137, 157, 179, 200], [116, 118, 119, 121, 123]]

    def __init__(self, frame: Frame, framesize: float = 1, **kwargs):
        self._grid = Grid((framesize, self.FRAME_CELLS, framesize, self.FRAME_CELLS), True)
        self._grid.mesh.transform(Transformation.from_frame(frame))
        super(FrameObject, self).__init__(grid=self._grid, **kwargs)

    def _read_lines_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        positions = []
        colors = []
        elements = []
        i = 0
        # TODO

        for i, (u, v) in enumerate(self._grid.mesh.edges()):
            positions.append(self.vertex_xyz[u])
            positions.append(self.vertex_xyz[v])
            # Color the axis:
            if i in self.AXIS_COLOR_INDICES[0]:
                colors.append(Color.red())
                colors.append(Color.red())
            elif i in self.AXIS_COLOR_INDICES[1]:
                colors.append(Color.green())
                colors.append(Color.green())
            else:
                colors.append(self.linescolor["_default"])
                colors.append(self.linescolor["_default"])
            elements.append([i + 0, i + 1])
            i += 2

        if self._grid.show_geidz:
            positions.append([0, 0, 0])
            positions.append([0, 0, (self._grid.dx + self._grid.dy) / 4])
            colors.append(Color.blue())
            colors.append(Color.blue())
            elements.append([i + 0, i + 1])

        return positions, colors, elements
