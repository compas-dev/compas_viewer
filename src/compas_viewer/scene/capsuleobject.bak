from compas.datastructures import Mesh
from compas.geometry import Capsule
from compas.geometry import Line

from .meshobject import MeshObject


class CapsuleObject(MeshObject):
    """Object for displaying COMPAS Capsule geometry."""

    def __init__(self, data, u=10, v=10, **kwargs):
        super().__init__(Mesh.from_shape(data, u=u, v=v), **kwargs)
        self.u = u
        self.v = v
        self._data = data

    def update(self):
        self._mesh = Mesh.from_shape(self._data, u=self.u, v=self.v)
        self.init()
        super().update()

    @property
    def properties(self):
        return ["u", "v"]

    @classmethod
    def create_default(cls) -> Capsule:
        return Capsule(Line((0, 0, 0), (0, 0, 1)), 0.5)
