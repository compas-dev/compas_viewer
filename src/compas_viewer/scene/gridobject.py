from os import PathLike
from os import path
from typing import Optional
from typing import Tuple
from typing import Union

from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Point
from compas.scene import GeometryObject
from freetype import FT_LOAD_FLAGS
from freetype import Face
from numpy import array
from numpy import linalg
from numpy import zeros
from OpenGL import GL

from compas_viewer.utilities import make_index_buffer
from compas_viewer.utilities import make_vertex_buffer

from .sceneobject import ViewerSceneObject


class Grid(Mesh):
    """
    The geometry class of the grid. A grid is a mesh with no faces and only edges.
    It is basically created by the :class:`compas.datastructures.Mesh.from_meshgrid`.

    Parameters
    ----------
    gridsize : tuple[float, int, float, int]
        The size of the grid in [dx, nx, dy, ny] format.
        See the :class:`compas.datastructures.Mesh.from_meshgrid` for more details.
    show_geidz : bool
        If True, the Z axis of the grid will be shown.

    Attributes
    ----------
    gridsize : tuple[float, float, int, int]
        The size of the grid in [dx, nx, dy, ny] format.
    show_geidz : bool
        If the Z axis of the grid is shown.
    """

    def __eq__(self, other):
        return isinstance(other, Grid) and self.gridsize == other.gridsize and self.show_geidz == other.show_geidz

    def __init__(
        self,
        gridsize: Tuple[float, int, float, int],
        show_geidz: bool,
    ):
        super().from_meshgrid(*gridsize)
        self.dx = gridsize[0]
        self.nx = gridsize[1]
        self.dy = gridsize[2]
        self.ny = gridsize[3]
        self.show_geidz = show_geidz


class TagObject(MeshObject, GeometryObject):
    """
    The scene object of the :class:`compas_viewer.scene.Grid` geometry.

    Parameters
    ----------
    grid : :class:`compas_viewer.scene.Grid`
        The grid geometry.
    color : :class:`compas.colors.Color`
        The color of the grid. Yet the XYZ axis are always red, green and blue.

    Attributes
    ----------
    grid : :class:`compas_viewer.scene.Grid`
        The grid geometry.
    color : :class:`compas.colors.Color`
        The color of the grid.
    """

    def __init__(self, grid: Grid, gridcolor: Color, **kwargs):
        super(TagObject, self).__init__(geometry=grid, **kwargs)
        self._grid = grid
        self.linescolor = gridcolor
        self.show_lines = self.is_visible
        self.show_points = False
        self.show_faces = False

    def _lines_data(self):
        positions = []
        colors = []
        elements = []
        color = self._color
        n = 0
        for x in range(-self._grid.nx, self._grid.nx + 1):
            if x == 0:
                positions.append([x * self.cell_size, -self._grid.nx * self.cell_size, 0])
                positions.append([x * self.cell_size, 0, 0])
                colors.append(color)
                colors.append(color)
                positions.append([x * self.cell_size, 0, 0])
                positions.append([x * self.cell_size, self._grid.nx * self.cell_size, 0])
                colors.append([0, 1, 0])
                colors.append([0, 1, 0])
                n = len(elements) * 2
                elements.append([n + 0, n + 1])
                elements.append([n + 2, n + 3])
            else:
                positions.append([x * self.cell_size, -self._grid.nx * self.cell_size, 0])
                positions.append([x * self.cell_size, self._grid.nx * self.cell_size, 0])
                colors.append(color)
                colors.append(color)
                n = len(elements) * 2
                elements.append([n, n + 1])

        for y in range(-self.y_cells, self.y_cells + 1):
            if y == 0:
                positions.append([-self.y_cells * self.cell_size, y * self.cell_size, 0])
                positions.append([0, y * self.cell_size, 0])
                colors.append(color)
                colors.append(color)
                positions.append([0, y * self.cell_size, 0])
                positions.append([self.y_cells * self.cell_size, y * self.cell_size, 0])
                colors.append([1, 0, 0])
                colors.append([1, 0, 0])
                n = len(elements) * 2
                elements.append([n + 0, n + 1])
                elements.append([n + 2, n + 3])
            else:
                positions.append([-self.y_cells * self.cell_size, y * self.cell_size, 0])
                positions.append([self.y_cells * self.cell_size, y * self.cell_size, 0])
                colors.append(color)
                colors.append(color)
                n = len(elements) * 2
                elements.append([n, n + 1])
        return positions, colors, elements

    def init(self):
        self.make_buffers()

        # Create uv plane
        x_size = self._grid.nx * self.cell_size
        y_size = self.y_cells * self.cell_size
        positions = [[-x_size, -y_size, 0], [x_size, -y_size, 0], [x_size, y_size, 0], [-x_size, y_size, 0]]
        color = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        elements = [[0, 1, 3], [1, 2, 3], [1, 0, 3], [2, 1, 3]]

        self._uvplane = {
            "positions": make_vertex_buffer(list(flatten(positions))),
            "colors": make_vertex_buffer(list(flatten(color))),
            "elements": make_index_buffer(list(flatten(elements))),
            "n": len(list(flatten(elements))),
        }

    def draw(self, shader):
        """Draw the object from its buffers"""
        shader.enable_attribute("position")
        shader.enable_attribute("color")
        shader.bind_attribute("position", self._lines_buffer["positions"])
        shader.bind_attribute("color", self._lines_buffer["colors"])
        shader.draw_lines(
            width=self.linewidth, elements=self._lines_buffer["elements"], n=self._lines_buffer["n"], background=True
        )
        shader.disable_attribute("position")
        shader.disable_attribute("color")

    def draw_plane(self, shader):
        shader.enable_attribute("position")
        shader.enable_attribute("color")
        shader.bind_attribute("position", self._uvplane["positions"])
        shader.bind_attribute("color", self._uvplane["colors"])
        shader.draw_triangles(elements=self._uvplane["elements"], n=self._uvplane["n"])
        shader.disable_attribute("position")
        shader.disable_attribute("color")
