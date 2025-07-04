from compas.geometry import Ellipse
from compas.geometry import Line
from compas.geometry import Point

from .geometryobject import GeometryObject


class EllipseObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Ellipse geometry."""

    geometry: Ellipse

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_lines = True

    @property
    def points(self) -> list[Point]:
        return [self.geometry.plane.point]

    @property
    def lines(self) -> list[Line]:
        return self.geometry.to_polyline(n=self.u).lines
