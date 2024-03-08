from typing import Optional

from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Sphere
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class SphereObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Sphere geometry.

    See Also
    --------
    :class:`compas.geometry.Sphere`
    """

    def __init__(self, sphere: Sphere, **kwargs):
        super().__init__(geometry=sphere, **kwargs)
        self.geometry: Sphere

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        return [self.geometry.frame.point]

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        return None

    @property
    def viewmesh(self) -> Mesh:
        """The mesh volume to be shown in the viewer."""
        return Mesh.from_shape(self.geometry, u=self.u, v=self.v, triangulated=True)
