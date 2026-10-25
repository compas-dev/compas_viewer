from typing import cast

from compas.geometry import Point

from .geometryobject import GeometryObject


class PointObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Point geometry."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.show_points = True

    @property
    def points(self) -> list[Point]:
        return [cast(Point, self.geometry)]
