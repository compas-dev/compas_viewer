from typing import List
from typing import Optional
from typing import Tuple

from compas.colors import Color
from compas.geometry import Point
from compas.scene import GeometryObject

from .sceneobject import ViewerSceneObject


class PointObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying COMPAS :class:`compas.geometry.Point` geometry."""

    def __init__(self, point: Point, **kwargs):
        super(PointObject, self).__init__(geometry=point, **kwargs)
        self.geometry: Point
        self._points_data = self._get_points_data()

    def _get_points_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        positions = [self.geometry]
        colors = [self.pointscolor["_default"]]
        elements = [[0]]
        return positions, colors, elements
