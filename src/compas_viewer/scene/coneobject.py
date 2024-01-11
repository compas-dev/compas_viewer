from math import pi

from compas.datastructures import Mesh
from compas.geometry import Cone

from .meshobject import MeshObject


class ConeObject(MeshObject):
    """Viewer scene object for displaying COMPAS Cone geometry.

    See Also
    --------
    :class:`compas.geometry.Cone`
    """

    def __init__(self, cone: Cone, **kwargs):
        self.u = kwargs.get("u", int(2 * pi * cone.radius / self.LINEARDEFLECTION))

        super(ConeObject, self).__init__(mesh=Mesh.from_shape(shape=cone, u=self.u), **kwargs)
