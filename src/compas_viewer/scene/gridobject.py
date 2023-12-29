from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import Tuple

from compas.colors import Color
from compas.data import Data
from compas.datastructures import Mesh
from compas.geometry import Point
from compas.geometry import Translation
from compas.scene import MeshObject as BaseMeshObject
from compas.utilities import flatten

from compas_viewer.scene.sceneobject import ViewerSceneObject
from compas_viewer.utilities import make_index_buffer
from compas_viewer.utilities import make_vertex_buffer

if TYPE_CHECKING:
    from compas_viewer.components.render.shaders import Shader


class Grid(Data):
    """
    The geometry class of the grid. A grid is a set of lines.

    Parameters
    ----------
    gridsize : Tuple[float, int, float, int]
        The size of the grid in [dx, nx, dy, ny] format.
        Notice that the `nx` and `ny` must be even numbers.
        See the :func:`compas.datastructures.Mesh.from_meshgrid()` for more details.
    show_geidz : bool
        If True, the Z axis of the grid will be shown.

    Attributes
    ----------
    gridsize : Tuple[float, float, int, int]
        The size of the grid in [dx, nx, dy, ny] format.
    dx : float
        The size of the grid in the X direction.
    nx : int
        The number of grid cells in the X direction.
    dy : float
        The size of the grid in the Y direction.
    ny : int
        The number of grid cells in the Y direction.
    show_geidz : bool
        If the Z axis of the grid is shown.
    mesh : :class:`compas.datastructures.Mesh`
        The mesh of the grid.

    """

    def __eq__(self, other):
        return (
            isinstance(other, Grid)
            and self.dx == other.dx
            and self.nx == other.nx
            and self.dy == other.dy
            and self.ny == other.ny
            and self.show_geidz == other.show_geidz
        )

    def __init__(
        self,
        gridsize: Tuple[float, int, float, int],
        show_geidz: bool,
    ):
        super(Grid, self).__init__()
        self.dx = gridsize[0]
        self.nx = gridsize[1]
        self.dy = gridsize[2]
        self.ny = gridsize[3]
        if self.nx % 2 == 1 or self.ny % 2 == 1:
            raise ValueError("gridsize : [dx, nx, dy, ny]: nx and ny must be even numbers.")
        self.show_geidz = show_geidz
        self.mesh = Mesh.from_meshgrid(*gridsize)
        self.mesh.transform(Translation.from_vector([-self.dx / 2, -self.dy / 2, 0]))

    @property
    def data(self):
        return {
            "gridsize": [self.dx, self.nx, self.dy, self.ny],
            "show_geidz": self.show_geidz,
        }


class GridObject(ViewerSceneObject, BaseMeshObject):
    """
    The scene object of the :class:`compas_viewer.scene.Grid` geometry.

    Parameters
    ----------
    grid : :class:`compas_viewer.scene.Grid`
        The grid geometry.

    Attributes
    ----------
    grid : :class:`compas_viewer.scene.Grid`
        The grid geometry.
    """

    def __init__(self, grid: Grid, **kwargs):
        super(GridObject, self).__init__(mesh=grid.mesh, **kwargs)
        self._grid = grid

        self._lines_data = self._get_lines_data()

    def _get_lines_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        positions = []
        colors = []
        elements = []
        i = 0

        for u, v in self._grid.mesh.edges():
            positions.append(self.vertex_xyz[u])
            positions.append(self.vertex_xyz[v])
            # Color the axis:
            if self.vertex_xyz[u][1] == 0 and self.vertex_xyz[v][1] == 0 and self.vertex_xyz[u][0] >= 0:
                colors.append(Color.red())
                colors.append(Color.red())
            elif self.vertex_xyz[u][0] == 0 and self.vertex_xyz[v][0] == 0 and self.vertex_xyz[u][1] >= 0:
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

    def init(self):
        self.make_buffers()

        # Create uv plane
        x_size = self._grid.nx * self._grid.dx
        y_size = self._grid.ny * self._grid.dy
        positions = [[-x_size, -y_size, 0], [x_size, -y_size, 0], [x_size, y_size, 0], [-x_size, y_size, 0]]
        color = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        elements = [[0, 1, 3], [1, 2, 3], [1, 0, 3], [2, 1, 3]]

        self._uvplane = {
            "positions": make_vertex_buffer(list(flatten(positions))),
            "colors": make_vertex_buffer(list(flatten(color))),
            "elements": make_index_buffer(list(flatten(elements))),
            "n": len(list(flatten(elements))),
        }

    def draw(self, shader: "Shader"):
        """Draw the object from its buffers"""
        assert self._lines_buffer is not None
        shader.enable_attribute("position")
        shader.enable_attribute("color")
        shader.bind_attribute("position", self._lines_buffer["positions"])
        shader.bind_attribute("color", self._lines_buffer["colors"])
        shader.draw_lines(
            width=self.lineswidth, elements=self._lines_buffer["elements"], n=self._lines_buffer["n"], background=True
        )
        shader.disable_attribute("position")
        shader.disable_attribute("color")

    def draw_plane(self, shader: "Shader"):
        shader.enable_attribute("position")
        shader.enable_attribute("color")
        shader.bind_attribute("position", self._uvplane["positions"])
        shader.bind_attribute("color", self._uvplane["colors"])
        shader.draw_triangles(elements=self._uvplane["elements"], n=self._uvplane["n"])
        shader.disable_attribute("position")
        shader.disable_attribute("color")

    def draw_vertices(self):
        pass

    def draw_edges(self):
        pass

    def draw_faces(self):
        pass
