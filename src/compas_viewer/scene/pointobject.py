from typing import cast

from compas.geometry import Point

from .geometryobject import GeometryObject


class PointObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Point geometry."""

    @property
    def points(self) -> list[Point]:
        return [cast(Point, self.geometry)]
