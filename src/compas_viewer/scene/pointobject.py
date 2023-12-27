from typing import List
from typing import Optional
from typing import Tuple

from compas.colors import Color
from compas.geometry import Point
from compas.scene import GeometryObject

from .sceneobject import ViewerSceneObject


class PointObject(ViewerSceneObject, GeometryObject):
    """Object for displaying COMPAS point geometry.

    Parameters
    ----------
    point : :class:`compas.geometry.Point`
        The point geometry.
    kwargs : dict, optional
        Additional options for the :class:`compas.viewer.scene.ViewerSceneObject`.

    Attributes
    ----------
    point : :class:`compas.geometry.Point`
        The point geometry.
    """

    def __init__(self, point: Point, **kwargs):
        super(PointObject, self).__init__(geometry=point, **kwargs)
        self._point = point

        self._points_data = self._get_points_data()

    def _get_points_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        positions = [self._point]
        colors = [self.pointscolor["_default"]]
        elements = [[0]]
        return positions, colors, elements

    @classmethod
    def create_default(cls) -> Point:
        return Point(0, 0, 0)
