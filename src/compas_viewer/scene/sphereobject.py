from math import pi

from compas.datastructures import Mesh
from compas.geometry import Sphere

from compas_viewer.scene.sceneobject import DataType

from .geometryobject import GeometryObject

class SphereObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Sphere geometry.

    See Also
    --------
    :class:`compas.geometry.Sphere`
    """

    def __init__(self, sphere: Sphere, u=None, v=None, **kwargs):
        self.u = u or int(2 * pi * sphere.radius / self.LINEARDEFLECTION)
        self.v = v or int(2 * pi * sphere.radius / self.LINEARDEFLECTION)
        super().__init__(sphere, mesh=Mesh.from_shape(sphere, u=self.u, v=self.v), **kwargs)

    def _read_lines_data(self) -> DataType:
        return None