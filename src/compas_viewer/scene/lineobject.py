from typing import List
from typing import Optional
from typing import Tuple

from compas.colors import Color
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject

from .sceneobject import ViewerSceneObject


class LineObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying COMPAS :class:`compas.geometry.Line` geometry."""

    def __init__(self, line: Line, **kwargs):
        super(LineObject, self).__init__(geometry=line, **kwargs)

    def _read_points_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        positions = [self.geometry.start, self.geometry.end]
        colors = [
            self.pointscolor.get(0, self.pointscolor["_default"]),  # type: ignore
            self.pointscolor.get(1, self.pointscolor["_default"]),  # type: ignore
        ]
        elements = [[0], [1]]
        return positions, colors, elements

    def _read_lines_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        positions = [self.geometry.start, self.geometry.end]
        colors = [
            self.pointscolor.get(0, self.pointscolor["_default"]),  # type: ignore
            self.pointscolor.get(1, self.pointscolor["_default"]),  # type: ignore
        ]
        elements = [[0, 1]]
        return positions, colors, elements

    def _read_frontfaces_data(self):
        """No frontfaces data exist for this geometry, Return None."""
        return None

    def _read_backfaces_data(self):
        """No backfaces data exist for this geometry, Return None."""
        return None
