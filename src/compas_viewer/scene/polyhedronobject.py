from typing import Optional

from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Polyhedron

from .geometryobject import GeometryObject


class PolyhedronObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Polyhedron geometry."""

    geometry: Polyhedron

    @property
    def points(self) -> Optional[list[Point]]:
        return self.geometry.points

    @property
    def lines(self) -> Optional[list[Line]]:
        return self.geometry.lines

    @property
    def viewmesh(self):
        mesh = self.geometry.to_mesh()
        vertices, faces = mesh.to_vertices_and_faces(triangulated=True)
        return Mesh.from_vertices_and_faces(vertices, faces)
