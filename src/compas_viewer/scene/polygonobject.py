from typing import Optional
from typing import Tuple

from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Polygon
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class PolygonObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Polygon geometry.

    See Also
    --------
    :class:`compas.geometry.Polygon`
    """

    def __init__(self, polygon: Polygon, **kwargs):
        super().__init__(geometry=polygon, **kwargs)
        self.geometry: Polygon
        self.show_lines = True

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        return self.geometry.points

    @property
    def lines(self) -> Optional[list[Line]]:
        return self.geometry.lines

    @property
    def viewmesh(self):
        """The mesh volume to be shown in the viewer."""
        return None
