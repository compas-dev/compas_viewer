from typing import Optional

from compas_occ.brep import OCCBrep

from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.itertools import pairwise
from compas.scene import GeometryObject
from compas.tolerance import TOL

from .geometryobject import GeometryObject as ViewerGeometryObject


class NurbsSurfaceObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS NurbsSurface geometry."""

    geometry: NurbsSurface

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._brep: OCCBrep = OCCBrep.from_surface(self.geometry)
        self._viewmesh, self._boundaries = self._brep.to_tesselation(TOL.lineardeflection)

    @property
    def points(self) -> Optional[list[Point]]:
        return self._brep.points

    @property
    def lines(self) -> Optional[list[Line]]:
        lines = []
        for polyline in self._boundaries:
            for pair in pairwise(polyline.points):
                lines.append(Line(*pair))

        return lines

    @property
    def viewmesh(self) -> Mesh:
        return self._viewmesh
