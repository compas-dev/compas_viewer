from math import pi
from typing import Optional

from compas.datastructures import Mesh
from compas.geometry import Cylinder
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class CylinderObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Cylinder geometry.

    See Also
    --------
    :class:`compas.geometry.Cylinder`
    """

    def __init__(self, cylinder: Cylinder, **kwargs):
        super().__init__(geometry=cylinder, **kwargs)
        self.geometry: Cylinder
        self.u = int(2 * pi * cylinder.radius / self.LINEARDEFLECTION)
        self.v = self.u

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        return None

    @property
    def lines(self) -> Optional[list[Line]]:
        return None

    @property
    def viewmesh(self):
        """The mesh volume to be shown in the viewer."""
        return Mesh.from_shape(self.geometry, u=self.u, triangulated=True)
