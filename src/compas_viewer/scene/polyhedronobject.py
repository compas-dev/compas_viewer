from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Polyhedron

from .geometryobject import GeometryObject


class PolyhedronObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Polyhedron geometry."""

    geometry: Polyhedron

    @property
    def points(self) -> list[Point]:
        return self.geometry.points

    @property
    def lines(self) -> list[Line]:
        return self.geometry.lines

    @property
    def viewmesh(self) -> tuple[list[Point], list[list[int]]]:
        return self.geometry.to_vertices_and_faces(triangulated=True)
