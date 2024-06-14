from typing import Optional

from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class LineObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Line geometry."""

    geometry: Line

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_lines = True

    @property
    def points(self) -> Optional[list[Point]]:
        return [self.geometry.start, self.geometry.end]

    @property
    def lines(self) -> Optional[list[Line]]:
        return [self.geometry]

    @property
    def viewmesh(self):
        return None
