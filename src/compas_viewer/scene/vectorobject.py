from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from compas.colors import Color
from compas.geometry import Point
from compas.geometry import Vector
from compas.scene import GeometryObject

from compas_viewer.components.render.shaders.shader import Shader

from .sceneobject import ViewerSceneObject


class VectorObject(ViewerSceneObject, GeometryObject):
    """Object for displaying COMPAS Vector.

    Parameters
    ----------
    vector : :class:`compas.geometry.Vector`
        The vector geometry.
    anchor : :class:`compas.geometry.Point`, optional
        The anchor point of the vector.
        Default is the origin point.
    **kwargs : Dict, optional
        Additional options for the :class:`compas_viewer.scene.ViewerSceneObject`.

    Attributes
    ----------
    ARROW_SIZE_FACTOR : float
        Fixed size of the arrow relative to the vector length.
    ARROW_FACE_INDICES : List[List[int]]
        Fixed indices for the arrow faces.

    """

    # Size of the arrow relative to the vector length.
    ARROW_SIZE_FACTOR = 0.1
    # Fixed indices for the arrow faces:
    ARROW_FACE_INDICES = [[6, 2, 3], [6, 3, 4], [6, 4, 5], [6, 5, 2], [2, 4, 3], [2, 5, 4]]

    def __init__(self, vector: Vector, anchor: Point = Point(0, 0, 0), **kwargs):
        super(VectorObject, self).__init__(geometry=vector, **kwargs)
        self._vector = vector
        self._anchor = anchor
        self.arrow_buffer: Dict[str, Any]
        self._lines_data = self._get_lines_data()

    def _get_lines_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        arrow_end = self._anchor + self._vector * (1 - self.ARROW_SIZE_FACTOR)
        arrow_width = self.ARROW_SIZE_FACTOR * self.ARROW_SIZE_FACTOR * self._vector.length
        positions = [
            self._anchor,  # Arrow start
            arrow_end,  # Arrow body end
            arrow_end + (self._vector.cross([1, 0, 0]) / self._vector.length) * arrow_width,  # Arrow corner 1
            arrow_end + (self._vector.cross([0, 1, 0]) / self._vector.length) * arrow_width,  # Arrow corner 2
            arrow_end + (self._vector.cross([-1, 0, 0]) / self._vector.length) * arrow_width,  # Arrow corner 3
            arrow_end + (self._vector.cross([0, -1, 0]) / self._vector.length) * arrow_width,  # Arrow corner 4
            self._anchor + self._vector,  # Arrow end
        ]

        colors = [self.linescolor["_default"]] * len(positions)
        elements = [[0, 1]]
        return positions, colors, elements

    def init(self):
        self.make_buffers()
        self.arrow_buffer = self.make_buffer_from_data([[], [], self.ARROW_FACE_INDICES])  # type: ignore

    def draw(self, shader: "Shader"):
        """Draw the object from its buffers"""
        assert self._lines_buffer is not None
        shader.enable_attribute("position")
        shader.enable_attribute("color")
        shader.bind_attribute("position", self._lines_buffer["positions"])
        shader.bind_attribute("color", self._lines_buffer["colors"])
        shader.draw_arrows(
            elements=self._lines_buffer["elements"], n=self._lines_buffer["n"], width=self.lineswidth, background=True
        )
        shader.draw_triangles(elements=self.arrow_buffer["elements"], n=self.arrow_buffer["n"], background=True)
        shader.disable_attribute("position")
        shader.disable_attribute("color")
