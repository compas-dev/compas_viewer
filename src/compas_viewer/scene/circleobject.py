import math

from compas.geometry import Circle
from compas.scene import GeometryObject
from compas.utilities import pairwise

from .sceneobject import DataType
from .sceneobject import ViewerSceneObject


class CircleObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying COMPAS :class:`compas.geometry.Circle` geometry."""

    def __init__(self, circle: Circle, **kwargs):
        self.geometry: Circle
        self.u = kwargs.get("u",int(circle.circumference / self.LINEARDEFLECTION))
        self.u_points = self._calculate_circle_points(circle)
        super().__init__(geometry=circle, **kwargs)

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

    def _read_points_data(self) -> DataType:
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

    def _read_lines_data(self) -> DataType:
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

    def _read_frontfaces_data(self):
        """No frontfaces data exist for this geometry, Return None."""
        return None

    def _read_backfaces_data(self):
        """No backfaces data exist for this geometry, Return None."""
        return None
