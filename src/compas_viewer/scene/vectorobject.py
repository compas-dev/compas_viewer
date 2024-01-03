from typing import Any
from typing import Dict

from compas.geometry import Point
from compas.geometry import Vector
from compas.scene import GeometryObject

from compas_viewer.utilities.gl import make_index_buffer
from compas_viewer.utilities.gl import make_vertex_buffer

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

    """

    def __init__(self, vector: Vector, anchor: Point = Point(0, 0, 0), **kwargs):
        super(VectorObject, self).__init__(geometry=vector, **kwargs)
        self._vector = vector
        self._anchor = anchor

        self._vector_data: Dict[str, Any]

    def init(self):
        self.make_buffers()

    def make_buffers(self):
        self._vector_data = {
            "positions": make_vertex_buffer(list(self._anchor)),
            "directions": make_vertex_buffer(list(self._vector)),
            "colors": make_vertex_buffer(self.linescolor["_default"]),
            "sizes": make_vertex_buffer([self.lineswidth]),
            "elements": make_index_buffer([0]),
            "n": 1,
        }

    def draw(self, shader):
        shader.enable_attribute("position")
        shader.enable_attribute("direction")
        shader.enable_attribute("color")
        shader.enable_attribute("size")
        shader.uniform4x4("transform", self.worldtransformation.matrix)
        shader.bind_attribute("position", self._vector_data["positions"])
        shader.bind_attribute("direction", self._vector_data["directions"])
        shader.bind_attribute("color", self._vector_data["colors"])
        shader.bind_attribute("size", self._vector_data["sizes"], step=1)
        shader.draw_arrows(elements=self._vector_data["elements"], n=self._vector_data["n"])
        shader.disable_attribute("position")
        shader.disable_attribute("direction")
        shader.disable_attribute("color")
        shader.disable_attribute("size")


