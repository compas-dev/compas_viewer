from compas.geometry import Frame
from compas.colors import Color
from .bufferobject import BufferObject


class FrameObject(BufferObject):
    """Object for displaying COMPAS Frame geometry."""

    def __init__(self, data, size=1.0, **kwargs):
        super().__init__(data, **kwargs)
        self.size = size
        self.show_points = True
        self.show_lines = True
        self.linecolors = [
            Color(1, 0, 0),
            Color(1, 0, 0),
            Color(0, 1, 0),
            Color(0, 1, 0),
            Color(0, 0, 1),
            Color(0, 0, 1),
        ]

    def _points_data(self):
        frame = self._data
        positions = [frame.point]
        colors = [self.pointcolor]
        elements = [[0]]
        return positions, colors, elements

    def _lines_data(self):
        frame = self._data
        positions = [
            frame.point,
            frame.point + (frame.xaxis * self.size),
            frame.point,
            frame.point + (frame.yaxis * self.size),
            frame.point,
            frame.point + (frame.zaxis * self.size),
        ]
        colors = self.linecolors
        elements = [[0, 1], [2, 3], [4, 5]]
        return positions, colors, elements

    @classmethod
    def create_default(cls) -> Frame:
        return Frame([0, 0, 0], [1, 0, 0], [0, 1, 0])
