from math import pi

from compas.datastructures import Mesh
from compas.geometry import Cylinder

from .meshobject import MeshObject


class CylinderObject(MeshObject):
    """Viewer scene object for displaying COMPAS Cylinder geometry.

    See Also
    --------
    :class:`compas.geometry.Cylinder`
    """

    def __init__(self, cylinder: Cylinder, **kwargs):
        self.u = kwargs.get("u", int(2 * pi * cylinder.radius / self.LINEARDEFLECTION))

        super(CylinderObject, self).__init__(mesh=Mesh.from_shape(cylinder, u=self.u), **kwargs)
