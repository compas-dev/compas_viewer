from typing import Optional

from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class PointObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Point geometry."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_points = True
        self.geometry: Point

    @property
    def points(self) -> Optional[list[Point]]:
        return [self.geometry]

    @property
    def lines(self) -> Optional[list[Line]]:
        return None

    @property
    def viewmesh(self):
        return None
