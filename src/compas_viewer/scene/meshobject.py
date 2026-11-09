from typing import Any
from typing import cast

from compas.colors import Color
from compas.geometry import centroid_points
from compas.geometry import is_coplanar
from compas.itertools import pairwise

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject

ColorDictValueType = dict[Any, Color] | Color | None


class MeshObject(ViewerSceneObject):
    """Viewer scene object for displaying COMPAS Mesh geometry.

    Parameters
    ----------
    mesh
        A COMPAS mesh.
    vertexcolor
        The vertex color. Defaults to the value of `pointcolor` in `viewer.config`.
    edgecolor
        The edge color. Defaults to the value of `linecolor` in `viewer.config`.
    facecolor
        The face color. Defaults to the value of `surfacecolor` in `viewer.config`.
    hide_coplanaredges
        True to hide the coplanar edges. Defaults to the value of `hide_coplanaredges` in `viewer.config`.
    use_vertexcolors
        True to use vertex color. Defaults to the value of `use_vertexcolors` in `viewer.config`.
    **kwargs
        Additional options for [ViewerSceneObject][compas_viewer.scene.ViewerSceneObject]
        and `compas.scene.MeshObject`.

    See Also
    --------
    `compas.datastructures.Mesh`

    """

    @property
    def pointcolor(self) -> Color:
        return cast(Color, self.vertexcolor)

    @pointcolor.setter
    def pointcolor(self, color: Color) -> None:
        self.vertexcolor = color

    @property
    def linecolor(self) -> Color:
        return cast(Color, self.edgecolor)

    @linecolor.setter
    def linecolor(self, color: Color) -> None:
        self.edgecolor = color

    @property
    def show_points(self) -> bool:
        return self.show_vertices

    @show_points.setter
    def show_points(self, show: bool) -> None:
        self.show_vertices = show

    @property
    def show_lines(self) -> bool:
        return self.show_edges

    @show_lines.setter
    def show_lines(self, show: bool) -> None:
        self.show_edges = show

    @property
    def pointsize(self) -> float:
        return self.vertexsize

    @pointsize.setter
    def pointsize(self, size: float) -> None:
        self.vertexsize = size

    @property
    def linewidth(self) -> float:
        return self.edgewidth

    @linewidth.setter
    def linewidth(self, size: float) -> None:
        self.edgewidth = size

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

        edgecolors = cast(dict[tuple[Any, Any], Color], self.edgecolor)
        for u, v in self.mesh.edges():
            color = edgecolors[(u, v)]
            if self.hide_coplanaredges:
                # hide the edge if neighbor faces are coplanar
                fkeys = self.mesh.edge_faces((u, v))
                if not self.mesh.is_edge_on_boundary((u, v)):
                    fkey1, fkey2 = fkeys
                    if fkey1 is None or fkey2 is None:
                        continue
                    ps = [
                        self.mesh.face_center(fkey1),
                        self.mesh.face_center(fkey2),
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

    def draw_vertices(self) -> list[object]:
        return []

    def draw_edges(self) -> list[object]:
        return []

    def draw_faces(self) -> list[object]:
        return []
