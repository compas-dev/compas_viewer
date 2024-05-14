from typing import Optional

from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas.itertools import pairwise
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class NurbsCurveObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS NurbsCurve geometry.

    See Also
    --------
    :class:`compas.geometry.NurbsCurve`
    """

    def __init__(self, curve: NurbsCurve, **kwargs):
        super().__init__(geometry=curve, **kwargs)
        self.geometry: NurbsCurve

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        return self.geometry.points

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        lines = []
        polyline = self.geometry.to_polyline()
        for pair in pairwise(polyline.points):
            lines.append(Line(*pair))

        return lines

    @property
    def viewmesh(self) -> Optional[Mesh]:
        """The mesh volume to be shown in the viewer."""
        pass
