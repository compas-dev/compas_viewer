from typing import Optional

from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Polyline
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class PolylineObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Polyline geometry.

    See Also
    --------
    :class:`compas.geometry.Polyline`
    """

    def __init__(self, polyline: Polyline, **kwargs):
        super().__init__(geometry=polyline, **kwargs)
        self.geometry: Polyline
        self.show_lines = True

    @property
    def points(self) -> Optional[list[Point]]:
        return self.geometry.points

    @property
    def lines(self) -> Optional[list[Line]]:
        return self.geometry.lines

    @property
    def viewmesh(self):
        return None
