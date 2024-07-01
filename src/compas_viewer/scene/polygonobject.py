from typing import Optional

from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Polygon
from compas.geometry import earclip_polygon

from .geometryobject import GeometryObject


class PolygonObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Polygon geometry."""

    geometry: Polygon

    @property
    def points(self) -> Optional[list[Point]]:
        return self.geometry.points

    @property
    def lines(self) -> Optional[list[Line]]:
        return self.geometry.lines

    @property
    def viewmesh(self):
        vertices = self.geometry.points
        faces = [list(range(len(vertices)))]
        faces = earclip_polygon(self.geometry)
        return Mesh.from_vertices_and_faces(vertices, faces)
