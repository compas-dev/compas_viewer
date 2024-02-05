from compas.colors import Color
from compas.geometry import Geometry
from compas.geometry import centroid_points
from compas.geometry import is_coplanar
from compas.scene import GeometryObject as BaseGeometryObject
from compas.utilities import pairwise
from compas.datastructures import Mesh

from .sceneobject import DataType
from .sceneobject import ViewerSceneObject


class GeometryObject(ViewerSceneObject, BaseGeometryObject):
    """Viewer scene object for displaying COMPAS geometry shapes."""

    def __init__(
        self,
        geometry: Geometry,
        mesh=None,
        hide_coplanaredges=True,
        pointcolor=None,
        linecolor=None,
        surfacecolor=None,
        doublesided=False,
        **kwargs
    ):
        super(GeometryObject, self).__init__(geometry=geometry, **kwargs)
        # TODO: use Polyhedron instead of Mesh
        self.mesh = mesh or Mesh.from_shape(geometry)
        self.hide_coplanaredges = hide_coplanaredges
        self.pointcolor = pointcolor or Color(0.2, 0.2, 0.2)
        self.linecolor = linecolor or Color(0.4, 0.4, 0.4)
        self.surfacecolor = surfacecolor or Color(0.8, 0.8, 0.8)
        self.doublesided = doublesided

    def _read_points_data(self) -> DataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for vertex in self.mesh.vertices():
            positions.append(self.mesh.vertex_coordinates(vertex))
            colors.append(self.pointcolor)
            elements.append([i])
            i += 1
        return positions, colors, elements

    def _read_lines_data(self) -> DataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for u, v in self.mesh.edges():
            color = self.linecolor
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

    def _read_frontfaces_data(self) -> DataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for face in self.mesh.faces():
            vertices = self.mesh.face_vertices(face)
            color = self.surfacecolor
            if len(vertices) == 3:
                a, b, c = vertices
                positions.append(self.mesh.vertex_coordinates(a))
                positions.append(self.mesh.vertex_coordinates(b))
                positions.append(self.mesh.vertex_coordinates(c))
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
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                    elements.append([i + 0, i + 1, i + 2])
                    i += 3

        return positions, colors, elements

    def _read_backfaces_data(self) -> DataType:
        positions = []
        colors = []
        elements = []

        if not self.doublesided:
            return positions, colors, elements

        i = 0
        faces = self.mesh.faces()
        for face in faces:
            vertices = self.mesh.face_vertices(face)[::-1]
            color = self.surfacecolor
            if len(vertices) == 3:
                a, b, c = vertices
                positions.append(self.mesh.vertex_coordinates(a))
                positions.append(self.mesh.vertex_coordinates(b))
                positions.append(self.mesh.vertex_coordinates(c))
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
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                    elements.append([i + 0, i + 1, i + 2])
                    i += 3

        return positions, colors, elements
