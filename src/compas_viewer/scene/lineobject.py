from typing import cast

from compas.geometry import Line
from compas.geometry import Point

from .geometryobject import GeometryObject


class LineObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Line geometry."""

    @property
    def points(self) -> list[Point] | None:
        line = cast(Line, self.geometry)
        return [line.start, line.end]

    @property
    def lines(self) -> list[Line] | None:
        return [cast(Line, self.geometry)]
