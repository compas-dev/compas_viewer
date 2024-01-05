from compas.datastructures import Mesh
from compas.geometry import Sphere
from .meshobject import MeshObject


class SphereObject(MeshObject):
    """Object for displaying COMPAS sphere geometry."""

    def __init__(self, data, u=16, v=16, **kwargs):
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
    def create_default(cls) -> Sphere:
        return Sphere((0, 0, 0), 1)
