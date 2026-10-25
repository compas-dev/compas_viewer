from typing import cast

from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Polyhedron
from compas.geometry import Tessellation

from .tessellationobject import TessellationObject


class PolyhedronObject(TessellationObject):
    """Viewer scene object for displaying COMPAS Polyhedron geometry."""

    @property
    def points(self) -> list[Point]:
        return cast(Polyhedron, self.geometry).points

    @property
    def lines(self) -> list[Line]:
        return cast(Polyhedron, self.geometry).lines

    @property
    def tessellation(self) -> Tessellation:
        return cast(Polyhedron, self.geometry).to_tessellation()
