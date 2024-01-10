from math import pi

from compas.datastructures import Mesh
from compas.geometry import Sphere

from .meshobject import MeshObject


class SphereObject(MeshObject):
    """Viewer scene object for displaying COMPAS :class:`compas.geometry.Sphere` geometry."""

    def __init__(self, sphere: Sphere, **kwargs):
        self.u = int(2 * pi * sphere.radius / self.LINEARDEFLECTION)
        self.v = self.u
        super(SphereObject, self).__init__(mesh=Mesh.from_shape(sphere, u=self.u, v=self.v), **kwargs)