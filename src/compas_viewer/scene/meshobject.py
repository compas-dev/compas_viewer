from compas.colors import Color
from compas.geometry import centroid_points
from compas.geometry import is_coplanar
from compas.utilities import pairwise

from .bufferobject import BufferObject


class MeshObject(BufferObject ):
    """Object for displaying COMPAS mesh data structures.

    Parameters
    ----------

    hide_coplanaredges : bool
        True to hide the coplanar edges.
    kwargs : dict, optional
        Additional visualization options for

    Attributes
    ----------
    facecolor : list
        Face color
    linecolor : list
        Line color
    pointcolor : list
        Face color
    linewidth : float
        Line width
    pointsize : float
        Point size
    hide_coplanaredges : bool
        True to hide the coplanar edges
    opacity : float
        The opacity of mesh
    vertices : list
        Subset of vertices to be displayed
    edges : list
        Subset of edges to be displayed
    faces : list
        Subset of faces to be displayed

    """

    def __init__(
        self, data, vertices=None, edges=None, faces=None, hide_coplanaredges=False, use_vertex_color=False, **kwargs
    ):
        super().__init__(data, **kwargs)
        self._mesh = data
        self.hide_coplanaredges = hide_coplanaredges
        self.use_vertex_color = use_vertex_color
        self.vertices = vertices
        self.edges = edges
        self.faces = faces

    def _points_data(self):
        mesh = self._mesh
        vertex_xyz = {vertex: mesh.vertex_attributes(vertex, "xyz") for vertex in mesh.vertices()}
        positions = []
        colors = []
        elements = []
        i = 0
        vertices = self.vertices or mesh.vertices()
        for vertex in vertices:
            positions.append(vertex_xyz[vertex])
            colors.append(self.pointcolors.get(vertex, self.pointcolor))
            elements.append([i])
            i += 1
        return positions, colors, elements

    def _lines_data(self):
        mesh = self._mesh
        vertex_xyz = {vertex: mesh.vertex_attributes(vertex, "xyz") for vertex in mesh.vertices()}
        positions = []
        colors = []
        elements = []
        i = 0
        edges = self.edges or mesh.edges()
        for u, v in edges:
            color = self.linecolors.get((u, v), self.linecolor)
            if self.hide_coplanaredges:
                # hide the edge if neighbor faces are coplanar
                fkeys = mesh.edge_faces(u, v)
                if not mesh.is_edge_on_boundary(u, v):
                    ps = [mesh.face_center(fkeys[0]), mesh.face_center(fkeys[1]), *mesh.edge_coordinates(u, v)]
                    if is_coplanar(ps, tol=1e-5):
                        continue
            positions.append(vertex_xyz[u])
            positions.append(vertex_xyz[v])
            colors.append(color)
            colors.append(color)
            elements.append([i + 0, i + 1])
            i += 2
        return positions, colors, elements

    def _frontfaces_data(self):
        mesh = self._mesh
        vertex_xyz = {vertex: mesh.vertex_attributes(vertex, "xyz") for vertex in mesh.vertices()}
        if self.use_vertex_color:
            vertex_color = {
                vertex: mesh.vertex_attribute(vertex, "color") or Color.grey() for vertex in mesh.vertices()
            }
        positions = []
        colors = []
        elements = []
        i = 0
        faces = self.faces or mesh.faces()
        for face in faces:
            vertices = mesh.face_vertices(face)
            color = self.facecolors.get(face, self.facecolor)
            if len(vertices) == 3:
                a, b, c = vertices
                positions.append(vertex_xyz[a])
                positions.append(vertex_xyz[b])
                positions.append(vertex_xyz[c])
                if self.use_vertex_color:
                    colors.append(vertex_color[a])
                    colors.append(vertex_color[b])
                    colors.append(vertex_color[c])
                else:
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                elements.append([i + 0, i + 1, i + 2])
                i += 3
            elif len(vertices) == 4:
                a, b, c, d = vertices
                positions.append(vertex_xyz[a])
                positions.append(vertex_xyz[b])
                positions.append(vertex_xyz[c])
                positions.append(vertex_xyz[a])
                positions.append(vertex_xyz[c])
                positions.append(vertex_xyz[d])
                if self.use_vertex_color:
                    colors.append(vertex_color[a])
                    colors.append(vertex_color[b])
                    colors.append(vertex_color[c])
                    colors.append(vertex_color[a])
                    colors.append(vertex_color[c])
                    colors.append(vertex_color[d])
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
                points = [vertex_xyz[vertex] for vertex in vertices]
                c = centroid_points(points)
                for a, b in pairwise(points + points[:1]):
                    positions.append(a)
                    positions.append(b)
                    positions.append(c)
                    if self.use_vertex_color:
                        colors.append(vertex_color[a])
                        colors.append(vertex_color[b])
                        colors.append(vertex_color[c])
                    else:
                        colors.append(color)
                        colors.append(color)
                        colors.append(color)
                    elements.append([i + 0, i + 1, i + 2])
                    i += 3
        return positions, colors, elements

    def _backfaces_data(self):
        mesh = self._mesh
        vertex_xyz = {vertex: mesh.vertex_attributes(vertex, "xyz") for vertex in mesh.vertices()}
        if self.use_vertex_color:
            vertex_color = {
                vertex: mesh.vertex_attribute(vertex, "color") or Color.grey() for vertex in mesh.vertices()
            }
        positions = []
        colors = []
        elements = []
        i = 0
        faces = self.faces or mesh.faces()
        for face in faces:
            vertices = mesh.face_vertices(face)[::-1]
            color = self.facecolors.get(face, self.facecolor)
            if len(vertices) == 3:
                a, b, c = vertices
                positions.append(vertex_xyz[a])
                positions.append(vertex_xyz[b])
                positions.append(vertex_xyz[c])
                if self.use_vertex_color:
                    colors.append(vertex_color[a])
                    colors.append(vertex_color[b])
                    colors.append(vertex_color[c])
                else:
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                elements.append([i + 0, i + 1, i + 2])
                i += 3
            elif len(vertices) == 4:
                a, b, c, d = vertices
                positions.append(vertex_xyz[a])
                positions.append(vertex_xyz[b])
                positions.append(vertex_xyz[c])
                positions.append(vertex_xyz[a])
                positions.append(vertex_xyz[c])
                positions.append(vertex_xyz[d])
                if self.use_vertex_color:
                    colors.append(vertex_color[a])
                    colors.append(vertex_color[b])
                    colors.append(vertex_color[c])
                    colors.append(vertex_color[a])
                    colors.append(vertex_color[c])
                    colors.append(vertex_color[d])
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
                points = [vertex_xyz[vertex] for vertex in vertices]
                c = centroid_points(points)
                for a, b in pairwise(points + points[:1]):
                    positions.append(a)
                    positions.append(b)
                    positions.append(c)
                    if self.use_vertex_color:
                        colors.append(vertex_color[a])
                        colors.append(vertex_color[b])
                        colors.append(vertex_color[c])
                    else:
                        colors.append(color)
                        colors.append(color)
                        colors.append(color)
                    elements.append([i + 0, i + 1, i + 2])
                    i += 3
        return positions, colors, elements
