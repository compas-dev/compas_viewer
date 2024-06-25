from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import centroid_points
from compas.geometry import is_coplanar
from compas.itertools import pairwise
from compas.scene import MeshObject as BaseMeshObject
from compas.scene.descriptors.colordict import ColorDictAttribute

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject

ColorDictValueType = Optional[Union[Dict[Any, Color], Color]]


class MeshObject(ViewerSceneObject, BaseMeshObject):
    """Viewer scene object for displaying COMPAS Mesh geometry.

    Parameters
    ----------
    mesh : :class:`compas.datastructures.Mesh`
        A COMPAS mesh.
    vertexcolor : Union[Dict[Any, :class:`compas.colors.Color`], :class:`compas.colors.Color`]], optional
        The vertex color. Defaults to the value of `pointcolor` in `viewer.config`.
    edgecolor : Union[Dict[Any, :class:`compas.colors.Color`], :class:`compas.colors.Color`]], optional
        The edge color. Defaults to the value of `linecolor` in `viewer.config`.
    facecolor : Union[Dict[Any, :class:`compas.colors.Color`], :class:`compas.colors.Color`]], optional
        The face color. Defaults to the value of `surfacecolor` in `viewer.config`.
    hide_coplanaredges : bool, optional
        True to hide the coplanar edges. Defaults to the value of `hide_coplanaredges` in `viewer.config`.
    use_vertexcolors : bool, optional
        True to use vertex color. Defaults to the value of `use_vertexcolors` in `viewer.config`.
    **kwargs : dict, optional
        Additional options for the :class:`compas_viewer.scene.ViewerSceneObject` and :class:`compas.scene.MeshObject`.

    Attributes
    ----------
    mesh : :class:`compas.datastructures.Mesh`
        The mesh data structure.
    use_vertexcolors : bool
        True to use vertex color. Defaults to False.
    hide_coplanaredges : bool
        True to hide the coplanar edges.

    See Also
    --------
    :class:`compas.datastructures.Mesh`
    """

    mesh: Mesh

    vertexcolor = ColorDictAttribute(default=Color(0.2, 0.2, 0.2))
    edgecolor = ColorDictAttribute(default=Color(0.2, 0.2, 0.2))
    facecolor = ColorDictAttribute(default=Color(0.9, 0.9, 0.9))

    mesh: Mesh

    def __init__(
        self,
        show_points: Optional[bool] = None,
        show_lines: Optional[bool] = None,
        pointsize: Optional[float] = None,
        linewidth: Optional[int] = None,
        hide_coplanaredges: Optional[bool] = None,
        use_vertexcolors: Optional[bool] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.show_points = show_points if show_points is not None else False
        self.show_lines = show_lines if show_lines is not None else True

        self.pointsize = pointsize if pointsize is not None else 6.0
        self.linewidth = linewidth if linewidth is not None else 1.0

        self.hide_coplanaredges = hide_coplanaredges if hide_coplanaredges is not None else False
        self.use_vertexcolors = use_vertexcolors if use_vertexcolors is not None else False

    @property
    def pointcolor(self) -> Color:
        return self.vertexcolor

    @pointcolor.setter
    def pointcolor(self, color: Color):
        self.vertexcolor = color

    @property
    def linecolor(self) -> Color:
        return self.edgecolor

    @linecolor.setter
    def linecolor(self, color: Color):
        self.edgecolor = color

    @property
    def show_points(self) -> bool:
        return self.show_vertices

    @show_points.setter
    def show_points(self, show: bool):
        self.show_vertices = show

    @property
    def show_lines(self) -> bool:
        return self.show_edges

    @show_lines.setter
    def show_lines(self, show: bool):
        self.show_edges = show

    @property
    def pointsize(self) -> float:
        return self.vertexsize

    @pointsize.setter
    def pointsize(self, size: float):
        self.vertexsize = size

    @property
    def linewidth(self) -> float:
        return self.edgesize

    @linewidth.setter
    def linewidth(self, size: float):
        self.edgesize = size

    def _read_points_data(self) -> ShaderDataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for vertex in self.mesh.vertices():
            positions.append(self.mesh.vertex_coordinates(vertex))
            colors.append(self.vertexcolor[vertex])
            elements.append([i])
            i += 1
        return positions, colors, elements

    def _read_lines_data(self) -> ShaderDataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for u, v in self.mesh.edges():
            color = self.edgecolor[(u, v)]
            if self.hide_coplanaredges:
                # hide the edge if neighbor faces are coplanar
                fkeys = self.mesh.edge_faces((u, v))
                if not self.mesh.is_edge_on_boundary((u, v)):
                    ps = [
                        self.mesh.face_center(fkeys[0]),
                        self.mesh.face_center(fkeys[1]),
                        *self.mesh.edge_coordinates((u, v)),
                    ]
                    if is_coplanar(ps, tol=1e-5):
                        continue
            positions.append(self.mesh.vertex_coordinates(u))
            positions.append(self.mesh.vertex_coordinates(v))
            colors.append(color)
            colors.append(color)
            elements.append([i + 0, i + 1])
            i += 2
        return positions, colors, elements

    def _read_frontfaces_data(self) -> ShaderDataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for face in self.mesh.faces():
            vertices = self.mesh.face_vertices(face)
            color = self.facecolor[face]
            if len(vertices) == 3:
                a, b, c = vertices
                positions.append(self.mesh.vertex_coordinates(a))
                positions.append(self.mesh.vertex_coordinates(b))
                positions.append(self.mesh.vertex_coordinates(c))
                if self.use_vertexcolors:
                    colors.append(self.vertexcolor[a])
                    colors.append(self.vertexcolor[b])
                    colors.append(self.vertexcolor[c])
                else:
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                elements.append([i + 0, i + 1, i + 2])
                i += 3
            elif len(vertices) == 4:
                a, b, c, d = vertices
                positions.append(self.mesh.vertex_coordinates(a))
                positions.append(self.mesh.vertex_coordinates(b))
                positions.append(self.mesh.vertex_coordinates(c))
                positions.append(self.mesh.vertex_coordinates(a))
                positions.append(self.mesh.vertex_coordinates(c))
                positions.append(self.mesh.vertex_coordinates(d))
                if self.use_vertexcolors:
                    colors.append(self.vertexcolor[a])
                    colors.append(self.vertexcolor[b])
                    colors.append(self.vertexcolor[c])
                    colors.append(self.vertexcolor[a])
                    colors.append(self.vertexcolor[c])
                    colors.append(self.vertexcolor[d])
                else:
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                elements.append([i + 0, i + 1, i + 2])
                elements.append([i + 3, i + 4, i + 5])
                i += 6
            else:
                points = [self.mesh.vertex_coordinates(vertex) for vertex in vertices]
                c = centroid_points(points)
                for a, b in pairwise(points + points[:1]):
                    positions.append(a)
                    positions.append(b)
                    positions.append(c)
                    if self.use_vertexcolors:
                        colors.append(self.vertexcolor[vertices[0]])
                        colors.append(self.vertexcolor[vertices[1]])
                        colors.append(self.vertexcolor[vertices[2]])
                    else:
                        colors.append(color)
                        colors.append(color)
                        colors.append(color)
                    elements.append([i + 0, i + 1, i + 2])
                    i += 3

        return positions, colors, elements

    def _read_backfaces_data(self) -> ShaderDataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for face in self.mesh.faces():
            vertices = self.mesh.face_vertices(face)[::-1]
            color = self.facecolor[face]
            if len(vertices) == 3:
                a, b, c = vertices
                positions.append(self.mesh.vertex_coordinates(a))
                positions.append(self.mesh.vertex_coordinates(b))
                positions.append(self.mesh.vertex_coordinates(c))
                if self.use_vertexcolors:
                    colors.append(self.vertexcolor[a])
                    colors.append(self.vertexcolor[b])
                    colors.append(self.vertexcolor[c])
                else:
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                elements.append([i + 0, i + 1, i + 2])
                i += 3
            elif len(vertices) == 4:
                a, b, c, d = vertices
                positions.append(self.mesh.vertex_coordinates(a))
                positions.append(self.mesh.vertex_coordinates(b))
                positions.append(self.mesh.vertex_coordinates(c))
                positions.append(self.mesh.vertex_coordinates(a))
                positions.append(self.mesh.vertex_coordinates(c))
                positions.append(self.mesh.vertex_coordinates(d))
                if self.use_vertexcolors:
                    colors.append(self.vertexcolor[a])
                    colors.append(self.vertexcolor[b])
                    colors.append(self.vertexcolor[c])
                    colors.append(self.vertexcolor[a])
                    colors.append(self.vertexcolor[c])
                    colors.append(self.vertexcolor[d])
                else:
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                elements.append([i + 0, i + 1, i + 2])
                elements.append([i + 3, i + 4, i + 5])
                i += 6
            else:
                points = [self.mesh.vertex_coordinates(vertex) for vertex in vertices]
                c = centroid_points(points)
                for a, b in pairwise(points + points[:1]):
                    positions.append(a)
                    positions.append(b)
                    positions.append(c)
                    if self.use_vertexcolors:
                        colors.append(self.vertexcolor[vertices[0]])
                        colors.append(self.vertexcolor[vertices[1]])
                        colors.append(self.vertexcolor[vertices[2]])
                    else:
                        colors.append(color)
                        colors.append(color)
                        colors.append(color)
                    elements.append([i + 0, i + 1, i + 2])
                    i += 3
        return positions, colors, elements

    def draw_vertices(self):
        return None

    def draw_edges(self):
        return None

    def draw_faces(self):
        return None
