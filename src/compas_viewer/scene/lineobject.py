from typing import List
from typing import Optional
from typing import Tuple

from compas.colors import Color
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject

from .sceneobject import ViewerSceneObject


class LineObject(ViewerSceneObject, GeometryObject):
    """Object for displaying COMPAS line geometry.

    Parameters
    ----------
    line : :class:`compas.geometry.Line`
        The line geometry.
    kwargs : dict, optional
        Additional options for the :class:`compas.viewer.scene.ViewerSceneObject`.

    Attributes
    ----------
    line : :class:`compas.geometry.Line`
        The line geometry.

    """

    def __init__(self, line: Line, **kwargs):
        super(LineObject, self).__init__(geometry=line, **kwargs)
        self._line = line

        self._points_data = self._get_points_data()
        self._lines_data = self._get_lines_data()
        self._frontfaces_data = self._get_frontfaces_data()
        self._backfaces_data = self._get_backfaces_data()

    def _get_points_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        if not self.show_points:
            return None
        line = self._line
        positions = [line.start, line.end]
        colors = [
            self.pointscolor.get(0, self.pointscolor["_default"]),  # type: ignore
            self.pointscolor.get(1, self.pointscolor["_default"]),  # type: ignore
        ]
        elements = [[0], [1]]
        return positions, colors, elements

    def _get_lines_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        line = self._line
        color = self.linescolor["_default"]
        positions = [line.start, line.end]
        colors = [color, color]
        elements = [[0, 1]]
        return positions, colors, elements

    def _get_frontfaces_data(self):
        pass

    def _get_backfaces_data(self):
        pass

    @classmethod
    def create_default(cls) -> Line:
        return Line([0, 0, 0], [0, 0, 1])
