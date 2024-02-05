from math import pi

from compas.datastructures import Mesh
from compas.geometry import Cylinder

from .geometryobject import GeometryObject


class CylinderObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Cylinder geometry.

    See Also
    --------
    :class:`compas.geometry.Cylinder`
    """

    def __init__(self, cylinder: Cylinder, u=None, **kwargs):
        self.u = u or int(2 * pi * cylinder.radius / self.LINEARDEFLECTION)
        mesh = Mesh.from_shape(cylinder, u=self.u)
        super().__init__(cylinder, mesh=mesh, **kwargs)
