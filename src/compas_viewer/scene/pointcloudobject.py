from compas.geometry import Point
from compas.geometry import Pointcloud

from .geometryobject import GeometryObject


class PointcloudObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Pointcloud geometry."""

    geometry: Pointcloud

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_points = True

    @property
    def points(self) -> list[Point]:
        return self.geometry.points

    @property
    def lines(self) -> None:
        return None

    @property
    def viewmesh(self):
        return None
