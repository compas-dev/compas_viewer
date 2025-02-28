from typing import Any

from compas.geometry import Point
from compas.geometry import Vector
from compas.scene import GeometryObject

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject


class VectorObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Vector geometry.

    Parameters
    ----------
    vector : :class:`compas.geometry.Vector`
        The vector geometry.
    anchor : :class:`compas.geometry.Point`, optional
        The anchor point of the vector.
        Default is the origin point.
    **kwargs : dict, optional
        Additional options for the :class:`compas_viewer.scene.ViewerSceneObject`.

    Notes
    -----
    The frame object is always unselectable.
    Apart from the :attr:`compas_viewer.scene.vectorobject.VectorObject.config.linewidth`
    that controls the width of the vector,
    the :attr:`compas_viewer.scene.vectorobject.VectorObject.config.vectorsize`
    (float 0-1) controls the size of the arrow.

    See Also
    --------
    :class:`compas.geometry.Vector`
    """

    geometry: Vector

    # Fixed indices for the arrow faces:
    ARROW_FACE_INDICES = [[6, 2, 3], [6, 3, 4], [6, 4, 5], [6, 5, 2], [2, 4, 3], [2, 5, 4]]

    def __init__(self, anchor: Point = Point(0, 0, 0), **kwargs):
        self._anchor = anchor
        super().__init__(**kwargs)
        self.arrow_buffer: dict[str, Any]
        self._lines_buffer: dict[str, Any]
        self._arrow_vertices: list[float] = []
        self._arrow_colors: list[float] = []

    def _calculate_arrow_buffer_data(self):
        arrow_end = self._anchor + self.geometry * (1 - self.viewer.config.vectorsize)
        arrow_width = 5 * self.viewer.config.vectorsize * self.viewer.config.vectorsize * self.geometry.length
        self._arrow_vertices = [
            self._anchor,  # Arrow start
            arrow_end,  # Arrow body end
            arrow_end + (self.geometry.cross([1, 0, 0]) / self.geometry.length) * arrow_width,  # Arrow corner 1
            arrow_end + (self.geometry.cross([0, 1, 0]) / self.geometry.length) * arrow_width,  # Arrow corner 2
            arrow_end + (self.geometry.cross([-1, 0, 0]) / self.geometry.length) * arrow_width,  # Arrow corner 3
            arrow_end + (self.geometry.cross([0, -1, 0]) / self.geometry.length) * arrow_width,  # Arrow corner 4
            self._anchor + self.geometry,  # Arrow end
        ]

        self._arrow_colors = [self.linecolor or self.viewer.config.linecolor] * len(self._arrow_vertices)

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

    def init(self):
        self._calculate_arrow_buffer_data()
        self._lines_data = self._read_lines_data() if self.show_lines else None
        self._frontfaces_data = self._read_frontfaces_data() if self.show_faces else None
