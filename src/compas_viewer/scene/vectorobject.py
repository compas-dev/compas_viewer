from typing import Any
from typing import Dict

from compas.geometry import Point
from compas.geometry import Vector
from compas.scene import GeometryObject
from numpy import array
from numpy.matlib import linalg

from compas_viewer.components.render.shaders.shader import Shader
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
    absolute_width : bool, optional
        If True, the line width of the vector sprite is calculated based on the distance between the tag and the camera.
        Default is False.
    **kwargs : Dict, optional
        Additional options for the :class:`compas_viewer.scene.ViewerSceneObject`.

    """

    def __init__(self, vector: Vector, anchor: Point = Point(0, 0, 0), absolute_width=False, **kwargs):
        super(VectorObject, self).__init__(geometry=vector, **kwargs)
        self._vector = vector
        self._anchor = anchor
        self._absolute_width = absolute_width

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

    def _calculate_vector_width(self, camera_position):
        if self._absolute_width:
            return int(
                ( self.lineswidth)
                / float(
                    linalg.norm(array(self._anchor) - array([camera_position.x, camera_position.y, camera_position.z]))
                )
            )

        else:
            return self.lineswidth

    def draw(self, shader: Shader):
        shader.enable_attribute("position")
        shader.enable_attribute("direction")
        shader.enable_attribute("color")
        shader.enable_attribute("size")
        shader.uniform4x4("transform", self.worldtransformation.matrix)
        shader.bind_attribute("position", self._vector_data["positions"])
        shader.bind_attribute("direction", self._vector_data["directions"])
        shader.bind_attribute("color", self._vector_data["colors"])
        if self._absolute_width:
            shader.bind_attribute("size", self._calculate_vector_width(self.viewer.render.camera.position), step=1)
        else:
            shader.bind_attribute("size", self._vector_data["sizes"], step=1)
        shader.draw_arrows(elements=self._vector_data["elements"], n=self._vector_data["n"])
        shader.disable_attribute("position")
        shader.disable_attribute("direction")
        shader.disable_attribute("color")
        shader.disable_attribute("size")
