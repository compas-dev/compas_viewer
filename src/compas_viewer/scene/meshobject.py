from typing import List
from typing import Tuple

from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Point
from compas.geometry import centroid_points
from compas.geometry import is_coplanar
from compas.scene import MeshObject as BaseMeshObject
from compas.utilities import pairwise

from .sceneobject import ViewerSceneObject


class MeshObject(ViewerSceneObject, BaseMeshObject):
    """Object for displaying COMPAS mesh data structures.

    Parameters
    ----------
    mesh : :class:`compas.datastructures.Mesh`
        A COMPAS mesh.
    hide_coplanaredges : bool, optional
        True to hide the coplanar edges. Defaults to False.
    use_vertex_color : bool, optional
        True to use vertex color. Defaults to True.
    kwargs : dict, optional
        Additional options for the :class:`compas.viewer.scene.sceneobject.ViewerSceneObject`.

    Attributes
    ----------
    mesh : :class:`compas.datastructures.Mesh`
        The mesh data structure.
    self.vertex_xyz : dict[int, list[float]]
        View coordinates of the vertices.
        Defaults to the real coordinates.
    color : :class:`compas.colors.Color`
        The base RGB color of the mesh.
    vertexcolor : :class:`compas.colors.ColorDict`
        Vertex colors.
    edgecolor : :class:`compas.colors.ColorDict`
        Edge colors.
    facecolor : :class:`compas.colors.ColorDict`
        Face colors.
    linewidth : float
        Line width.
    pointsize : float
        Point size.
    hide_coplanaredges : bool
        True to hide the coplanar edges.
    opacity : float
        The opacity of mesh.
    """

    def __init__(self, mesh: Mesh, hide_coplanaredges: bool = False, use_vertex_color: bool = True, **kwargs):
        super(MeshObject, self).__init__(mesh=mesh, **kwargs)
        self._mesh = mesh
        self.hide_coplanaredges = hide_coplanaredges
        self.use_vertex_color = use_vertex_color
        self.vertexcolor = {vertex: self._mesh.vertex_attribute(vertex, "color") for vertex in self._mesh.vertices()}

    def _points_data(self) -> Tuple[List[Point], List[Color], List[int]]:
        positions = []
        colors = []
        elements = []
        i = 0

        for vertex in self._mesh.vertices():
            assert isinstance(vertex, int)
            positions.append(self.vertex_xyz[vertex])
            colors.append(self.pointcolors.get(vertex, self.pointcolor))
            elements.append([i])
            i += 1
        return positions, colors, elements

    def _lines_data(self) -> Tuple[List[Point], List[Color], List[int]]:
        positions = []
        colors = []
        elements = []
        i = 0

        for u, v in self._mesh.edges():
            color = self.linecolors.get((u, v), self.linecolor)
            if self.hide_coplanaredges:
                # hide the edge if neighbor faces are coplanar
                fkeys = self._mesh.edge_faces((u, v))
                if not self._mesh.is_edge_on_boundary((u, v)):
                    ps = [
                        self._mesh.face_center(fkeys[0]),
                        self._mesh.face_center(fkeys[1]),
                        *self._mesh.edge_coordinates((u, v)),
                    ]
                    if is_coplanar(ps, tol=1e-5):
                        continue
            positions.append(self.vertex_xyz[u])
            positions.append(self.vertex_xyz[v])
            colors.append(color)
            colors.append(color)
            elements.append([i + 0, i + 1])
            i += 2
        return positions, colors, elements

    def _frontfaces_data(self):
        positions = []
        colors = []
        elements = []
        i = 0

        for face in self._mesh.faces():
            vertices = self._mesh.face_vertices(face)
            assert isinstance(face, int)

            color = self.facecolors.get(face, self.facecolor)
            if len(vertices) == 3:
                a, b, c = vertices
                positions.append(self.vertex_xyz[a])
                positions.append(self.vertex_xyz[b])
                positions.append(self.vertex_xyz[c])
                if self.use_vertex_color:
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
                positions.append(self.vertex_xyz[a])
                positions.append(self.vertex_xyz[b])
                positions.append(self.vertex_xyz[c])
                positions.append(self.vertex_xyz[a])
                positions.append(self.vertex_xyz[c])
                positions.append(self.vertex_xyz[d])
                if self.use_vertex_color:
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
                points = [self.vertex_xyz[vertex] for vertex in vertices]
                c = centroid_points(points)
                for a, b in pairwise(points + points[:1]):
                    positions.append(a)
                    positions.append(b)
                    positions.append(c)
                    if self.use_vertex_color:
                        colors.append(self.vertexcolor[a])
                        colors.append(self.vertexcolor[b])
                        colors.append(self.vertexcolor[c])
                    else:
                        colors.append(color)
                        colors.append(color)
                        colors.append(color)
                    elements.append([i + 0, i + 1, i + 2])
                    i += 3
        return positions, colors, elements

    def _backfaces_data(self):
        if self.use_vertex_color:
            self.vertexcolor = {
                vertex: self._mesh.vertex_attribute(vertex, "color") or Color.grey() for vertex in self._mesh.vertices()
            }
        positions = []
        colors = []
        elements = []
        i = 0
        faces = self._mesh.faces()
        for face in faces:
            vertices = self._mesh.face_vertices(face)[::-1]
            assert isinstance(face, int)
            color = self.facecolors.get(face, self.facecolor)
            if len(vertices) == 3:
                a, b, c = vertices
                positions.append(self.vertex_xyz[a])
                positions.append(self.vertex_xyz[b])
                positions.append(self.vertex_xyz[c])
                if self.use_vertex_color:
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
                positions.append(self.vertex_xyz[a])
                positions.append(self.vertex_xyz[b])
                positions.append(self.vertex_xyz[c])
                positions.append(self.vertex_xyz[a])
                positions.append(self.vertex_xyz[c])
                positions.append(self.vertex_xyz[d])
                if self.use_vertex_color:
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
                points = [self.vertex_xyz[vertex] for vertex in vertices]
                c = centroid_points(points)
                for a, b in pairwise(points + points[:1]):
                    positions.append(a)
                    positions.append(b)
                    positions.append(c)
                    if self.use_vertex_color:
                        colors.append(self.vertexcolor[a])
                        colors.append(self.vertexcolor[b])
                        colors.append(self.vertexcolor[c])
                    else:
                        colors.append(color)
                        colors.append(color)
                        colors.append(color)
                    elements.append([i + 0, i + 1, i + 2])
                    i += 3
        return positions, colors, elements

    def draw_vertices(self, vertices=None, color=None, text=None):
        pass

    def draw_edges(self, edges=None, color=None, text=None):
        pass

    def draw_faces(self, faces=None, color=None, text=None):
        pass
