from typing import cast

from compas.geometry import Point
from compas.geometry import Pointcloud

from .geometryobject import GeometryObject


class PointcloudObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Pointcloud geometry."""

    @property
    def points(self) -> list[Point]:
        return cast(Pointcloud, self.geometry).points
