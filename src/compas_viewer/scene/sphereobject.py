from math import pi

from compas.datastructures import Mesh
from compas.geometry import Sphere

from .meshobject import MeshObject


class SphereObject(MeshObject):
    """Viewer scene object for displaying COMPAS Sphere geometry.

    See Also
    --------
    :class:`compas.geometry.Sphere`
    """

    def __init__(self, sphere: Sphere, **kwargs):
        self.u = kwargs.get("u", int(2 * pi * sphere.radius / self.LINEARDEFLECTION))
        self.v = kwargs.get("v", int(2 * pi * sphere.radius / self.LINEARDEFLECTION))
        super(SphereObject, self).__init__(mesh=Mesh.from_shape(sphere, u=self.u, v=self.v), **kwargs)
