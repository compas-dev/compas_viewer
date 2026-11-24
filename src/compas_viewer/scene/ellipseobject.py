from typing import cast

from compas.geometry import Ellipse
from compas.geometry import Line
from compas.geometry import Point

from .geometryobject import GeometryObject


class EllipseObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Ellipse geometry."""

    @property
    def points(self) -> list[Point]:
        return [cast(Ellipse, self.geometry).plane.point]

    @property
    def lines(self) -> list[Line]:
        return cast(Ellipse, self.geometry).to_polyline(n=cast(int, self.u)).lines
