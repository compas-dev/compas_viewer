from collections.abc import Iterable
from typing import cast

from compas.geometry import Brep
from compas.geometry import Line
from compas.geometry import NurbsSurface
from compas.itertools import pairwise

from .geometryobject import GeometryObject


class NurbsSurfaceObject(GeometryObject):
    """Viewer scene object for displaying COMPAS NurbsSurface geometry."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        geometry = cast(NurbsSurface, self.geometry)
        self._brep: Brep = geometry.to_brep()
        self._viewmesh, self._boundaries = self._brep.to_tesselation()

    @property
    def points(self) -> list[Iterable[float]]:
        """Boundary vertices of the surface Brep."""
        return [point for point in self._brep.points]

    @property
    def lines(self) -> list[Iterable[Iterable[float]]]:
        """Discretized boundary curves of the surface Brep."""
        lines: list[Iterable[Iterable[float]]] = []
        for polyline in self._boundaries:
            for pair in pairwise(polyline.points):
                lines.append(Line(*pair))

        return lines

    @property
    def viewmesh(self) -> tuple[list[Iterable[float]], list[list[int]]]:
        """Triangulated view mesh of the surface Brep."""
        vertices, faces = self._viewmesh.to_vertices_and_faces(triangulated=True)
        return [vertex for vertex in vertices], [face for face in faces]
