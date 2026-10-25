from typing import cast

from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Polygon
from compas.geometry import Tessellation

from .tessellationobject import TessellationObject


class PolygonObject(TessellationObject):
    """Viewer scene object for displaying COMPAS Polygon geometry."""

    @property
    def points(self) -> list[Point]:
        return cast(Polygon, self.geometry).points

    @property
    def lines(self) -> list[Line]:
        return cast(Polygon, self.geometry).lines

    @property
    def tessellation(self) -> Tessellation:
        return cast(Polygon, self.geometry).tessellation
