from typing import Any
from typing import Dict

from compas.geometry import Point
from compas.geometry import Vector
from compas.scene import GeometryObject

from compas_viewer.components.render.shaders.shader import Shader

from .sceneobject import DataType
from .sceneobject import ViewerSceneObject


class VectorObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying COMPAS :class:`compas.geometry.Vector` geometry.

    Parameters
    ----------
    vector : :class:`compas.geometry.Vector`
        The vector geometry.
    anchor : :class:`compas.geometry.Point`, optional
        The anchor point of the vector.
        Default is the origin point.
    **kwargs : Dict, optional
        Additional options for the :class:`compas_viewer.scene.ViewerSceneObject`.

    Notes
    -----
    The frame object is always unselectable.
    Apart from the :attr:`compas_viewer.scene.vectorobject.VectorObject.config.lineswidth`
    that controls the width of the vector,
    the :attr:`compas_viewer.scene.vectorobject.VectorObject.config.vectorsize`
    (float 0-1) controls the size of the arrow.
    """

    # Fixed indices for the arrow faces:
    ARROW_FACE_INDICES = [[6, 2, 3], [6, 3, 4], [6, 4, 5], [6, 5, 2], [2, 4, 3], [2, 5, 4]]

    def __init__(self, vector: Vector, anchor: Point = Point(0, 0, 0), **kwargs):
        self._anchor = anchor
        super(VectorObject, self).__init__(geometry=vector, **kwargs)
        self.arrow_buffer: Dict[str, Any]

    def _read_lines_data(self) -> DataType:
        arrow_end = self._anchor + self.geometry * (1 - self.config.vectorsize)
        arrow_width = self.config.vectorsize * self.config.vectorsize * self.geometry.length
        positions = [
            self._anchor,  # Arrow start
            arrow_end,  # Arrow body end
            arrow_end + (self.geometry.cross([1, 0, 0]) / self.geometry.length) * arrow_width,  # Arrow corner 1
            arrow_end + (self.geometry.cross([0, 1, 0]) / self.geometry.length) * arrow_width,  # Arrow corner 2
            arrow_end + (self.geometry.cross([-1, 0, 0]) / self.geometry.length) * arrow_width,  # Arrow corner 3
            arrow_end + (self.geometry.cross([0, -1, 0]) / self.geometry.length) * arrow_width,  # Arrow corner 4
            self._anchor + self.geometry,  # Arrow end
        ]

        colors = [self.linescolor["_default"]] * len(positions)
        elements = [[0, 1]]
        return positions, colors, elements

    def init(self):
        self._lines_data = self._read_lines_data() if self.show_lines else None
        self.make_buffers()
        self.arrow_buffer = self.make_buffer_from_data([[], [], self.ARROW_FACE_INDICES])  # type: ignore

    def draw(self, shader: "Shader"):
        """Draw the object from its buffers"""
        assert self._lines_buffer is not None
        if self.worldtransformation is not None:
            shader.uniform4x4("transform", self.worldtransformation.matrix)
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
