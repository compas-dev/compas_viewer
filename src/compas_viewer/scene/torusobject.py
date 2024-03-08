from math import pi
from typing import Optional

from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Torus
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class TorusObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Torus geometry.

    See Also
    --------
    :class:`compas.geometry.Torus`
    """

    def __init__(self, torus: Torus, **kwargs):
        super().__init__(geometry=torus, **kwargs)
        self.geometry: Torus
        self.u = int(2 * pi * torus.radius_axis / self.LINEARDEFLECTION)
        self.v = int(2 * pi * torus.radius_pipe / self.LINEARDEFLECTION)

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        return [self.geometry.plane.point]

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        pass

    @property
    def viewmesh(self):
        """The mesh volume to be shown in the viewer."""
        return Mesh.from_shape(self.geometry, u=self.u, v=self.v)
