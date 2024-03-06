from compas.geometry import Polyline
from compas.scene import GeometryObject
from compas.utilities import pairwise

from .sceneobject import DataType
from .sceneobject import ViewerSceneObject


class PolylineObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Polyline geometry.

    See Also
    --------
    :class:`compas.geometry.Polyline`
    """

    def __init__(self, polyline: Polyline, **kwargs):
        super().__init__(geometry=polyline, **kwargs)
        self.geometry: Polyline

    def _read_points_data(self) -> DataType:
        positions = [point for point in self.geometry.points]
        colors = [
            self.pointscolor.get(i, self.pointscolor["_default"])  # type: ignore
            for i, _ in enumerate(self.geometry.points)
        ]
        elements = [[i] for i in range(len(positions))]
        return positions, colors, elements

    def _read_lines_data(self) -> DataType:
        positions = []
        colors = []
        elements = []
        if self.geometry.is_closed:
            lines = pairwise(self.geometry.points + [self.geometry.points[0]])
        else:
            lines = pairwise(self.geometry.points)
        count = 0
        for i, (pt1, pt2) in enumerate(lines):
            positions.append(pt1)
            positions.append(pt2)
            colors.append(self.pointscolor.get(i, self.pointscolor["_default"]))  # type: ignore
            colors.append(self.pointscolor.get(i, self.pointscolor["_default"]))  # type: ignore
            elements.append([count, count + 1])
            count += 2
        return positions, colors, elements
