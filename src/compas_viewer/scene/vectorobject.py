from typing import Any
from typing import cast

from compas.colors import Color
from compas.geometry import Point
from compas.geometry import Vector
from compas.scene import GeometryObject

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject


class VectorObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Vector geometry.

    Parameters
    ----------
    vector
        The vector geometry.
    anchor
        The anchor point of the vector.
        Default is the origin point.
    **kwargs
        Additional scene-object options.

    Notes
    -----
    The frame object is always unselectable.
    ``linewidth`` controls the width of the vector and ``vectorsize`` controls
    the size of the arrow.

    """

    # Fixed indices for the arrow faces:
    ARROW_FACE_INDICES = [[6, 2, 3], [6, 3, 4], [6, 4, 5], [6, 5, 2], [2, 4, 3], [2, 5, 4]]

    def __init__(self, anchor: Point | None = None, **kwargs: Any) -> None:
        self._anchor = anchor or Point(0, 0, 0)
        super().__init__(**kwargs)
        self.arrow_buffer: dict[str, Any]
        self._lines_buffer: dict[str, Any]
        self._arrow_vertices: list[Point] = []
        self._arrow_colors: list[Color] = []

    def _calculate_arrow_buffer_data(self) -> None:
        vector = cast(Vector, self.geometry)
        arrow_end = self._anchor + vector * (1 - self.viewer.config.vectorsize)
        arrow_width = 5 * self.viewer.config.vectorsize * self.viewer.config.vectorsize * vector.length
        self._arrow_vertices = [
            self._anchor,  # Arrow start
            arrow_end,  # Arrow body end
            arrow_end + (vector.cross([1, 0, 0]) / vector.length) * arrow_width,  # Arrow corner 1
            arrow_end + (vector.cross([0, 1, 0]) / vector.length) * arrow_width,  # Arrow corner 2
            arrow_end + (vector.cross([-1, 0, 0]) / vector.length) * arrow_width,  # Arrow corner 3
            arrow_end + (vector.cross([0, -1, 0]) / vector.length) * arrow_width,  # Arrow corner 4
            self._anchor + vector,  # Arrow end
        ]

        self._arrow_colors = [self.linecolor or self.viewer.config.display.linecolor] * len(self._arrow_vertices)

    def _read_lines_data(self) -> ShaderDataType:
        positions = self._arrow_vertices
        colors = self._arrow_colors
        elements = [[0, 1]]
        return positions, colors, elements

    def _read_frontfaces_data(self) -> ShaderDataType:
        positions = self._arrow_vertices
        colors = self._arrow_colors
        elements = self.ARROW_FACE_INDICES
        return positions, colors, elements

    def init(self) -> None:
        self._calculate_arrow_buffer_data()
        super().init()
