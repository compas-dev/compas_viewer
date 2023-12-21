from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Frame

from .meshobject import MeshObject


class BoxObject(MeshObject):
    """Object for displaying COMPAS box geometry."""

    def __init__(self, data, **kwargs):
        super().__init__(Mesh.from_shape(data), **kwargs)
        self._data = data

    def update(self):
        self._mesh = Mesh.from_shape(self._data)
        super().update()

    @classmethod
    def create_default(cls) -> Box:
        return Box(Frame.worldXY(), 1.0, 1.0, 1.0)
