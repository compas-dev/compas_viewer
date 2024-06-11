from typing import Optional

from compas.geometry import Circle
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class CircleObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Circle geometry.

    See Also
    --------
    :class:`compas.geometry.Circle`
    """

    def __init__(self, circle: Circle, **kwargs):
        super().__init__(geometry=circle, **kwargs)
        self.geometry: Circle
        self.show_lines = True

    @property
    def points(self) -> Optional[list[Point]]:
        return [self.geometry.center]

    @property
    def lines(self) -> Optional[list[Line]]:
        return self.geometry.to_polyline(n=self.u).lines

    @property
    def viewmesh(self):
        return None
