import math
from typing import Optional
from typing import Tuple

from compas.geometry import Circle
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject
from compas.utilities import pairwise

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
        self.u = int(circle.circumference / self.LINEARDEFLECTION)
        self.show_lines = True

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

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        return [self.geometry.center]

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        return [
            Line(*pair)
            for pair in pairwise(
                self._calculate_circle_points(self.geometry) + [self._calculate_circle_points(self.geometry)[0]]
            )
        ]

    @property
    def surfaces(self) -> Optional[list[Tuple[Point, Point, Point]]]:
        """The surface to be shown in the viewer. Currently only triangles are supported."""
        pass
