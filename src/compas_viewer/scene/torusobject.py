from math import pi

from compas.datastructures import Mesh
from compas.geometry import Torus

from .meshobject import MeshObject


class TorusObject(MeshObject):
    """Viewer scene object for displaying COMPAS Torus geometry.

    See Also
    --------
    :class:`compas.geometry.Torus`
    """

    def __init__(self, torus: Torus, **kwargs):
        self.u = kwargs.get("u", int(2 * pi * torus.radius_axis / self.LINEARDEFLECTION))
        self.v = kwargs.get("v", int(2 * pi * torus.radius_pipe / self.LINEARDEFLECTION))

        super().__init__(mesh=Mesh.from_shape(torus, u=self.u, v=self.v), **kwargs)
