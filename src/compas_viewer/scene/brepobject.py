from compas_occ.brep import OCCBrep

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

    geometry: OCCBrep

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._viewmesh, self._boundaries = self.geometry.to_tesselation(TOL.lineardeflection)

    @property
    def points(self) -> list[Point]:
        return self.geometry.points

    @property
    def lines(self) -> list[Line]:
        lines = []
        for polyline in self._boundaries:
            lines += polyline.lines
        return lines

    @property
    def viewmesh(self) -> tuple[list[Point], list[list[int]]]:
        return self._viewmesh.to_vertices_and_faces(triangulated=True)
