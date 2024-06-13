from compas.geometry import Point
from compas.geometry import Pointcloud
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class PointcloudObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Pointcloud geometry."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_points = True
        self.geometry: Pointcloud

    @property
    def points(self) -> list[Point]:
        return self.geometry.points

    @property
    def lines(self) -> None:
        return None

    @property
    def viewmesh(self):
        return None
