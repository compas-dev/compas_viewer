from compas.utilities import flatten
from .bufferobject import BufferObject


class NurbsSurfaceObject(BufferObject):
    """Object for displaying COMPAS NurbsSurface geometry."""

    def __init__(self, surface, u=100, v=100, **kwargs):
        super().__init__(surface, **kwargs)
        self._data = surface
        self._triangles = [list(point) for triangle in surface.to_triangles(nu=u, nv=v) for point in triangle]
        self.u = u
        self.v = v

    def update(self):
        self._triangles = [
            list(point) for triangle in self._data.to_triangles(nu=self.u, nv=self.v) for point in triangle
        ]
        self.init()
        super().update()

    def _points_data(self):
        positions = [list(pt) for pt in flatten(self._data.points)]
        colors = [self.pointcolor for _ in positions]
        elements = [[i] for i in range(len(positions))]
        return positions, colors, elements

    def _lines_data(self):
        positions = [list(pt) for pt in flatten(self._data.points)]
        colors = [self.linecolor for _ in positions]
        count = 0
        indexes = []
        for row in self._data.points:
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

    def _frontfaces_data(self):
        positions = self._triangles
        colors = [self.facecolor] * len(self._triangles)
        elements = [[i * 3 + 0, i * 3 + 1, i * 3 + 2] for i in range(int(len(self._triangles) / 3))]
        return positions, colors, elements

    def _backfaces_data(self):
        positions = self._triangles[::-1]
        colors = [self.facecolor] * len(self._triangles)
        elements = [[i * 3 + 0, i * 3 + 1, i * 3 + 2] for i in range(int(len(self._triangles) / 3))]
        return positions, colors, elements

    @property
    def properties(self):
        return ["u", "v"]
