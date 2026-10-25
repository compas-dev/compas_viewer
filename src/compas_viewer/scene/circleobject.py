from typing import cast

from compas.geometry import Circle
from compas.geometry import Line
from compas.geometry import Point

from .geometryobject import GeometryObject


class CircleObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Circle geometry."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.show_lines = True

    @property
    def points(self) -> list[Point]:
        return [cast(Circle, self.geometry).center]

    @property
    def lines(self) -> list[Line]:
        return cast(Circle, self.geometry).to_polyline(n=cast(int, self.u)).lines
