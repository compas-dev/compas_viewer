from compas.geometry import Line
from compas.scene import GeometryObject

from .sceneobject import DataType
from .sceneobject import ViewerSceneObject


class LineObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Line geometry.

    See Also
    --------
    :class:`compas.geometry.Line`
    """

    def __init__(self, line: Line, **kwargs):
        super(LineObject, self).__init__(geometry=line, **kwargs)

    def _read_points_data(self) -> DataType:
        positions = [self.geometry.start, self.geometry.end]
        colors = [
            self.pointscolor.get(0, self.pointscolor["_default"]),  # type: ignore
            self.pointscolor.get(1, self.pointscolor["_default"]),  # type: ignore
        ]
        elements = [[0], [1]]
        return positions, colors, elements

    def _read_lines_data(self) -> DataType:
        positions = [self.geometry.start, self.geometry.end]
        colors = [
            self.pointscolor.get(0, self.pointscolor["_default"]),  # type: ignore
            self.pointscolor.get(1, self.pointscolor["_default"]),  # type: ignore
        ]
        elements = [[0, 1]]
        return positions, colors, elements
