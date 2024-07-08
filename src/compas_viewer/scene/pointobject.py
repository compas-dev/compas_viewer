from typing import Optional

from compas.geometry import Line
from compas.geometry import Point

from .geometryobject import GeometryObject


class PointObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Point geometry."""

    geometry: Point

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_points = True

    @property
    def points(self) -> Optional[list[Point]]:
        return [self.geometry]

    @property
    def lines(self) -> Optional[list[Line]]:
        return None

    @property
    def viewmesh(self):
        return None
