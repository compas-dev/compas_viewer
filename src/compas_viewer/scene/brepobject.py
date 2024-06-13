from typing import Optional

from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject
from compas.tolerance import TOL

from .geometryobject import GeometryObject as ViewerGeometryObject


class BRepObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS OCCBrep geometry.

    Attributes
    ----------
    brep : :class:`compas_occ.brep.OCCBrep`
        The compas_occ Brep object.
    mesh : :class:`compas.datastructures.Mesh`
        The mesh representation of the Brep.

    See Also
    --------
    :class:`compas_occ.brep.Brep`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._viewmesh, self._boundaries = self.geometry.to_tesselation(TOL.lineardeflection)

    @property
    def points(self) -> Optional[list[Point]]:
        return self.geometry.points

    @property
    def lines(self) -> Optional[list[Line]]:
        lines = []
        for polyline in self._boundaries:
            lines += polyline.lines
        return lines

    @property
    def viewmesh(self) -> Mesh:
        return self._viewmesh
