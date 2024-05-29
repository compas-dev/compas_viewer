# from compas.datastructures import Mesh
# from compas.geometry import Line
# from compas.geometry import Point
from compas.geometry import Sphere

from .shapeobject import ShapeObject


class SphereObject(ShapeObject):
    """Viewer scene object for displaying COMPAS Sphere geometry.

    See Also
    --------
    :class:`compas.geometry.Sphere`
    """

    def __init__(self, sphere: Sphere, **kwargs):
        super().__init__(geometry=sphere, **kwargs)
        self.geometry: Sphere

    #     self.geometry.resolution_u = self.u
    #     self.geometry.resolution_v = self.v

    # @property
    # def points(self) -> list[Point]:
    #     return self.geometry.vertices

    # @property
    # def lines(self) -> list[list[float, float, float], list[float, float, float]]:
    #     vertices = self.geometry._vertices
    #     lines = [(vertices[u], vertices[v]) for u, v in self.geometry.edges]
    #     return lines

    # @property
    # def triangles(self) -> list[list[list[float, float, float], list[float, float, float], list[float, float, float]]]:
    #     vertices = self.geometry._vertices
    #     triangles = [(vertices[u], vertices[v], vertices[w]) for u, v, w in self.geometry.triangles]
    #     return triangles

    # @property
    # def viewmesh(self):
    #     vertices = self.geometry._vertices
    #     faces = self.geometry.triangles
    #     mesh = Mesh.from_vertices_and_faces(vertices, faces)
    #     return mesh
