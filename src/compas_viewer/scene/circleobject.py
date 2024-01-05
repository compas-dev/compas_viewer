import math
from typing import List
from typing import Optional
from typing import Tuple

from compas.colors import Color
from compas.geometry import Circle
from compas.geometry import Point
from compas.scene import GeometryObject
from compas.utilities import pairwise

from .sceneobject import ViewerSceneObject


class CircleObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying COMPAS :class:`compas.geometry.Circle` geometry."""

    def __init__(self, circle: Circle, **kwargs):
        super().__init__(geometry=circle, close=True, **kwargs)

        self.geometry: Circle

        self.u = int(circle.circumference / self.LINEARDEFLECTION)
        self.u_points = self._calculate_circle_points(self.geometry)

        self._points_data = self._get_points_data()
        self._lines_data = self._get_lines_data()

    def _calculate_circle_points(self, circle):
        return [
            circle.frame.to_world_coordinates(
                [
                    math.cos(i * math.pi * 2 / self.u) * circle.radius,
                    math.sin(i * math.pi * 2 / self.u) * circle.radius,
                    0,
                ]
            )
            for i in range(self.u)
        ]

    def _get_points_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        if not self.show_points:
            return None
        positions = []
        colors = []
        elements = []
        i = 0

        for i, u_point in enumerate(self.u_points):
            positions.append(u_point)
            colors.append(self.pointscolor.get(i, self.pointscolor["_default"]))  # type: ignore
            elements.append([i])
            i += 1

        return positions, colors, elements

    def _get_lines_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        if not self.show_lines:
            return None
        positions = []
        colors = []
        elements = []
        i = 0
        count = 0
        lines = pairwise(self.u_points + [self.u_points[0]])
        count = 0
        for i, (pt1, pt2) in enumerate(lines):
            positions.append(pt1)
            positions.append(pt2)
            colors.append(self.pointscolor.get(i, self.pointscolor["_default"]))  # type: ignore
            colors.append(self.pointscolor.get(i, self.pointscolor["_default"]))  # type: ignore
            elements.append([count, count + 1])
            count += 2
        return positions, colors, elements
