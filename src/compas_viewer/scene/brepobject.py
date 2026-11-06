from collections.abc import Iterable
from typing import cast

from compas.geometry import Brep
from compas.geometry import Tessellation
from compas.itertools import pairwise
from compas.typing import PointLike
from compas.typing import RealInput
from compas.typing import VerticesFaces

from .geometryobject import GeometryObject as ViewerGeometryObject


class BRepObject(ViewerGeometryObject):
    """Viewer scene object for displaying COMPAS Brep geometry.

    The object consumes the stable `compas.geometry.Brep` wrapper. The active
    Brep backend provides tessellation and topology through COMPAS plugins.

    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._tessellation: Tessellation | None = None

    def refresh_data(self) -> None:
        """Regenerate one coherent tessellation and all render buffers.

        A Brep is mutable. Re-tessellating at the refresh boundary keeps its
        boundary curves and face buffers synchronized with the current Brep
        while avoiding duplicate tessellation work during one refresh.

        """
        geometry = cast(Brep, self.geometry)
        self._tessellation = geometry.to_tessellation()
        super().refresh_data()

    @property
    def tessellation(self) -> Tessellation:
        """Tessellation used by the current render-data refresh."""
        if self._tessellation is None:
            geometry = cast(Brep, self.geometry)
            self._tessellation = geometry.to_tessellation()
        return self._tessellation

    @property
    def points(self) -> list[Iterable[RealInput]]:
        """Boundary vertices of the Brep."""
        geometry = cast(Brep, self.geometry)
        return [point for point in geometry.points]

    @property
    def lines(self) -> list[tuple[PointLike, PointLike]]:
        """Discretized boundary curves of the Brep."""
        return [segment for polyline in self.tessellation.polylines for segment in pairwise(polyline)]

    @property
    def viewmesh(self) -> VerticesFaces:
        """Triangulated view mesh of the Brep."""
        return self.tessellation.vertices, self.tessellation.triangles
