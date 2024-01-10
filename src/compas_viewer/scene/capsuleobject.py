from math import pi

from compas.datastructures import Mesh
from compas.geometry import Capsule

from .meshobject import MeshObject


class CapsuleObject(MeshObject):
    """Viewer scene object for displaying COMPAS :class:`compas.geometry.Capsule` geometry."""

    def __init__(self, capsule: Capsule, **kwargs):
        self.u =kwargs.get("u", int(2 * pi * capsule.radius / self.LINEARDEFLECTION))

        super(CapsuleObject, self).__init__(mesh=Mesh.from_shape(capsule, u=self.u), **kwargs)
