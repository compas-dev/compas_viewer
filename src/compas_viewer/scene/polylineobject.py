from typing import cast

from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Polyline

from .geometryobject import GeometryObject


class PolylineObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Polyline geometry."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.show_lines = True

    @property
    def points(self) -> list[Point] | None:
        return cast(Polyline, self.geometry).points

    @property
    def lines(self) -> list[Line] | None:
        return cast(Polyline, self.geometry).lines
