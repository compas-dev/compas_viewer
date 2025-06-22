from typing import Optional

from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas.itertools import pairwise

from .geometryobject import GeometryObject


class NurbsCurveObject(GeometryObject):
    """Viewer scene object for displaying COMPAS NurbsCurve geometry."""

    geometry: NurbsCurve

    @property
    def points(self) -> Optional[list[Point]]:
        return self.geometry.points

    @property
    def lines(self) -> Optional[list[Line]]:
        lines = []
        polyline = self.geometry.to_polyline()
        for pair in pairwise(polyline.points):
            lines.append(Line(*pair))
        return lines
