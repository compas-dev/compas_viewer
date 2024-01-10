from typing import Optional

from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import centroid_points
from compas.geometry import is_coplanar
from compas.scene import MeshObject as BaseMeshObject
from compas.utilities import pairwise

from .sceneobject import DataType
from .sceneobject import ViewerSceneObject


class MeshObject(ViewerSceneObject, BaseMeshObject):
    """Viewer scene object for displaying COMPAS :class:`compas.datastructures.Mesh` geometry.

    Parameters
    ----------
    mesh : :class:`compas.datastructures.Mesh`
        A COMPAS mesh.
    hide_coplanaredges : bool, optional
        True to hide the coplanar edges. It will override the value in the config file.
    use_vertexcolors : bool, optional
        True to use vertex color. It will override the value in the config file.
    **kwargs : Dict, optional
        Additional options for the :class:`compas_viewer.scene.ViewerSceneObject`.

    Attributes
    ----------
    mesh : :class:`compas.datastructures.Mesh`
        The mesh data structure.
    vertex_xyz : Dict[int, List[float]]
        View coordinates of the vertices.
        Defaults to the real coordinates.
    vertexcolor : :class:`compas.colors.ColorDict`
        Vertex colors.
    use_vertexcolors : bool
        True to use vertex color. Defaults to False.
    hide_coplanaredges : bool
        True to hide the coplanar edges.
    """

    def __init__(
        self, mesh: Mesh, hide_coplanaredges: Optional[bool] = None, use_vertexcolors: Optional[bool] = None, **kwargs
    ):
        self._mesh = mesh
        super(MeshObject, self).__init__(mesh=mesh, **kwargs)
        self.hide_coplanaredges = (
            hide_coplanaredges if hide_coplanaredges is not None else self.config.hide_coplanaredges
        )
        self.use_vertexcolors = use_vertexcolors if use_vertexcolors is not None else self.config.use_vertexcolors
        self.vertexcolor = {
            vertex: self._mesh.vertex_attribute(vertex, "color")
            or self.facescolor.get(vertex, self.facescolor["_default"])  # type: ignore
            for vertex in self._mesh.vertices()
        }

    @property
    def vertex_xyz(self):
        """
        Override :class:`compas.scene.MeshObject`'s property since the viewer does not need to transform the vertices.
        Transformation is handled by the shader.
        """
        if self._vertex_xyz is None:
            points = self.mesh.vertices_attributes("xyz")  # type: ignore
            self._vertex_xyz = dict(zip(self.mesh.vertices(), points))  # type: ignore
        return self._vertex_xyz

    def _read_points_data(self) -> DataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for vertex in self._mesh.vertices():
            assert isinstance(vertex, int)
            positions.append(self.vertex_xyz[vertex])
            colors.append(self.pointscolor.get(vertex, self.pointscolor["_default"]))  # type: ignore
            elements.append([i])
            i += 1
        return positions, colors, elements

    def _read_lines_data(self) -> DataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for u, v in self._mesh.edges():
            color = self.linescolor.get((u, v), self.linescolor["_default"])  # type: ignore
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

    def _read_frontfaces_data(self) -> DataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for face in self._mesh.faces():
            vertices = self._mesh.face_vertices(face)
            assert isinstance(face, int)
            color = self.facescolor.get(face, self.facescolor["_default"])  # type: ignore
            if len(vertices) == 3:
                a, b, c = vertices
                positions.append(self.vertex_xyz[a])
                positions.append(self.vertex_xyz[b])
                positions.append(self.vertex_xyz[c])
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
                positions.append(self.vertex_xyz[a])
                positions.append(self.vertex_xyz[b])
                positions.append(self.vertex_xyz[c])
                positions.append(self.vertex_xyz[a])
                positions.append(self.vertex_xyz[c])
                positions.append(self.vertex_xyz[d])
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
                points = [self.vertex_xyz[vertex] for vertex in vertices]
                c = centroid_points(points)
                for a, b in pairwise(points + points[:1]):
                    positions.append(a)
                    positions.append(b)
                    positions.append(c)
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

        return positions, colors, elements

    def _read_backfaces_data(self) -> DataType:
        if self.use_vertexcolors:
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
            color = self.facescolor.get(face, self.facescolor["_default"])  # type: ignore
            if len(vertices) == 3:
                a, b, c = vertices
                positions.append(self.vertex_xyz[a])
                positions.append(self.vertex_xyz[b])
                positions.append(self.vertex_xyz[c])
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
                positions.append(self.vertex_xyz[a])
                positions.append(self.vertex_xyz[b])
                positions.append(self.vertex_xyz[c])
                positions.append(self.vertex_xyz[a])
                positions.append(self.vertex_xyz[c])
                positions.append(self.vertex_xyz[d])
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
                points = [self.vertex_xyz[vertex] for vertex in vertices]
                c = centroid_points(points)
                for a, b in pairwise(points + points[:1]):
                    positions.append(a)
                    positions.append(b)
                    positions.append(c)
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
        return positions, colors, elements

    def draw_vertices(self):
        pass

    def draw_edges(self):
        pass

    def draw_faces(self):
        pass
