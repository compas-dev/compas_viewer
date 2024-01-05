from compas.datastructures import Mesh
from compas.geometry import Plane
from compas.geometry import Circle
from compas.geometry import Cone

from .meshobject import MeshObject


class ConeObject(MeshObject):
    """Object for displaying COMPAS cone geometry."""

    def __init__(self, data, u=16, **kwargs):
        super().__init__(Mesh.from_shape(data, u=u), **kwargs)
        self.u = u
        self._data = data

    def update(self):
        self._mesh = Mesh.from_shape(self._data, u=self.u)
        self.init()
        super().update()

    @property
    def properties(self):
        return ["u"]

    @classmethod
    def create_default(cls) -> Cone:
        return Cone(Circle(Plane([0, 0, 0], [0, 0, 1]), 0.5), 1)
