from math import pi
from typing import Optional

from compas.datastructures import Mesh
from compas.geometry import Cone
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class ConeObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Cone geometry.

    See Also
    --------
    :class:`compas.geometry.Cone`
    """

    def __init__(self, cone: Cone, **kwargs):
        super().__init__(geometry=cone, **kwargs)
        self.geometry: Cone
        self.u = int(2 * pi * cone.radius / self.LINEARDEFLECTION)
        self.v = self.u

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        return None

    @property
    def lines(self) -> Optional[list[Line]]:
        return None

    @property
    def viewmesh(self) -> Mesh:
        """The mesh volume to be shown in the viewer."""
        return Mesh.from_shape(self.geometry, u=self.u, v=self.v)
