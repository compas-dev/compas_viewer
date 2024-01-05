from typing import List
from typing import Optional
from typing import Tuple

from compas.colors import Color
from compas.geometry import Point
from compas.geometry import Polygon
from compas.geometry import centroid_points
from compas.scene import GeometryObject
from compas.utilities import pairwise
from .polylineobject import PolylineObject
from .sceneobject import ViewerSceneObject


class PolygonObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying COMPAS :class:`compas.geometry.Polygon` geometry."""

    def __init__(self, polygon: Polygon, **kwargs):
        super(PolygonObject, self).__init__(geometry=polygon, **kwargs)
        self.geometry: Polygon

        self._points_data = self._get_points_data()
        self._lines_data = self._get_lines_data()

    def _get_points_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        if not self.show_points:
            return None
        positions = [point for point in self.geometry.points]
        colors = [self.pointscolor.get(i, self.pointscolor["_default"]) for i, _ in enumerate(self.geometry.points)]  # type: ignore
        elements = [[i] for i in range(len(positions))]
        return positions, colors, elements

    def _get_lines_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        if not self.show_lines:
            return None
        positions = []
        colors = []
        elements = []
        lines = pairwise(self.geometry.points + [self.geometry.points[0]])
        count = 0
        for i, (pt1, pt2) in enumerate(lines):
            positions.append(pt1)
            positions.append(pt2)
            colors.append(self.pointscolor.get(i, self.pointscolor["_default"]))  # type: ignore
            colors.append(self.pointscolor.get(i, self.pointscolor["_default"]))  # type: ignore
            elements.append([count, count + 1])
            count += 2
        return positions, colors, elements

    def _frontfaces_data(self):
        if not self.show_face:
            return
        positions = []
        colors = []
        elements = []
        points = self._data.points
        color = self.facecolor
        if len(points) == 3:
            a, b, c = points
            positions.append(a)
            positions.append(b)
            positions.append(c)
            colors.append(color)
            colors.append(color)
            colors.append(color)
            elements.append([0, 1, 2])
        elif len(points) == 4:
            a, b, c, d = points
            positions.append(a)
            positions.append(b)
            positions.append(c)
            positions.append(a)
            positions.append(c)
            positions.append(d)
            colors.append(color)
            colors.append(color)
            colors.append(color)
            colors.append(color)
            colors.append(color)
            colors.append(color)
            elements.append([0, 1, 2])
            elements.append([3, 4, 5])
        else:
            c = centroid_points(points)
            i = 0
            for a, b in pairwise(points + points[:1]):
                positions.append(a)
                positions.append(b)
                positions.append(c)
                colors.append(color)
                colors.append(color)
                colors.append(color)
                elements.append([i + 0, i + 1, i + 2])
                i += 3
        return positions, colors, elements

    def _backfaces_data(self):
        if not self.show_face:
            return
        positions = []
        colors = []
        elements = []
        points = self._data.points[::-1]
        color = self.facecolor
        if len(points) == 3:
            a, b, c = points
            positions.append(a)
            positions.append(b)
            positions.append(c)
            colors.append(color)
            colors.append(color)
            colors.append(color)
            elements.append([0, 1, 2])
        elif len(points) == 4:
            a, b, c, d = points
            positions.append(a)
            positions.append(b)
            positions.append(c)
            positions.append(a)
            positions.append(c)
            positions.append(d)
            colors.append(color)
            colors.append(color)
            colors.append(color)
            colors.append(color)
            colors.append(color)
            colors.append(color)
            elements.append([0, 1, 2])
            elements.append([3, 4, 5])
        else:
            c = centroid_points(points)
            i = 0
            for a, b in pairwise(points + points[:1]):
                positions.append(a)
                positions.append(b)
                positions.append(c)
                colors.append(color)
                colors.append(color)
                colors.append(color)
                elements.append([i + 0, i + 1, i + 2])
                i += 3
        return positions, colors, elements
