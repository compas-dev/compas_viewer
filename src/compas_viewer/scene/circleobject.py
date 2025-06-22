from compas.geometry import Circle
from compas.geometry import Line
from compas.geometry import Point

from .geometryobject import GeometryObject


class CircleObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Circle geometry."""

    geometry: Circle

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_lines = True

    @property
    def points(self) -> list[Point]:
        return [self.geometry.center]

    @property
    def lines(self) -> list[Line]:
        return self.geometry.to_polyline(n=self.u).lines
