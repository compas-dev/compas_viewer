from collections.abc import Iterable
from typing import cast

from compas.geometry import Brep
from compas.geometry import Tessellation
from compas.itertools import pairwise
from compas.typing import PointLike
from compas.typing import RealInput

from .geometryobject import GeometryObject as ViewerGeometryObject


class BRepObject(ViewerGeometryObject):
    """Viewer scene object for displaying COMPAS Brep geometry.

    The object consumes the stable `compas.geometry.Brep` wrapper. The active
    Brep backend provides tessellation and topology through COMPAS plugins.

    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        geometry = cast(Brep, self.geometry)
        self._tessellation: Tessellation = geometry.to_tessellation()

    @property
    def points(self) -> list[Iterable[RealInput]]:
        """Boundary vertices of the Brep."""
        geometry = cast(Brep, self.geometry)
        return [point for point in geometry.points]

    @property
    def lines(self) -> list[tuple[PointLike, PointLike]]:
        """Discretized boundary curves of the Brep."""
        return [segment for polyline in self._tessellation.polylines for segment in pairwise(polyline)]

    @property
    def viewmesh(self) -> tuple[list[Iterable[float]], list[list[int]]]:
        """Triangulated view mesh of the Brep."""
        return [vertex for vertex in self._tessellation.vertices], [list(triangle) for triangle in self._tessellation.triangles]
