from typing import cast

from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas.itertools import pairwise

from .geometryobject import GeometryObject


class NurbsCurveObject(GeometryObject):
    """Viewer scene object for displaying COMPAS NurbsCurve geometry."""

    @property
    def points(self) -> list[Point] | None:
        return cast(NurbsCurve, self.geometry).points

    @property
    def lines(self) -> list[Line] | None:
        lines = []
        polyline = cast(NurbsCurve, self.geometry).to_polyline()
        for pair in pairwise(polyline.points):
            lines.append(Line(*pair))
        return lines
