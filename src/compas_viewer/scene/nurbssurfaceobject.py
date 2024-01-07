from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.scene import GeometryObject
from compas.utilities import flatten

from .sceneobject import DataType
from .sceneobject import ViewerSceneObject


class NurbsSurfaceObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying COMPAS :class:`compas.geometry.NurbsSurface` geometry."""

    def __init__(self, surface: NurbsSurface, **kwargs):
        super().__init__(geometry=surface, **kwargs)

        # LINEARDEFLECTION not implemented in NurbsSurface.
        self.u = int(16 + (0 * self.LINEARDEFLECTION))
        self.v = int(16 + (0 * self.LINEARDEFLECTION))

        self._triangles = [list(point) for triangle in surface.to_triangles(nu=self.u, nv=self.v) for point in triangle]

    def _read_points_data(self) -> DataType:
        positions = [Point(*pt) for pt in flatten(self.geometry.points)]
        colors = [self.pointscolor.get(i, self.pointscolor["_default"]) for i in range(len(positions))]  # type: ignore
        elements = [[i] for i in range(len(positions))]
        return positions, colors, elements

    def _read_lines_data(self) -> DataType:
        positions = [Point(*pt) for pt in flatten(self.geometry.points)]
        colors = [self.linescolor.get(i, self.linescolor["_default"]) for i in range(len(positions))]  # type: ignore
        count = 0

        indexes = []
        for row in self.geometry.points:
            row_i = []
            for _ in range(len(row)):
                row_i.append(count)
                count += 1
            indexes.append(row_i)
        elements = []
        for row in indexes:
            for i in range(len(row) - 1):
                elements.append([row[i], row[i + 1]])
        for col in zip(*indexes):
            for i in range(len(col) - 1):
                elements.append([col[i], col[i + 1]])
        return positions, colors, elements

    def _read_frontfaces_data(self) -> DataType:
        positions = [Point(*triangle) for triangle in self._triangles]
        colors = [
            self.facescolor.get(i, self.facescolor["_default"]) for i in range(len(self._triangles))  # type: ignore
        ]
        elements = [[i * 3 + 0, i * 3 + 1, i * 3 + 2] for i in range(int(len(self._triangles) / 3))]
        return positions, colors, elements

    def _read_backfaces_data(self):
        positions = self._triangles[::-1]
        colors = [
            self.facescolor.get(i, self.facescolor["_default"]) for i in range(len(self._triangles))  # type: ignore
        ]
        elements = [[i * 3 + 0, i * 3 + 1, i * 3 + 2] for i in range(int(len(self._triangles) / 3))]
        return positions, colors, elements
