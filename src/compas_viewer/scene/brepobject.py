from collections.abc import Iterable
from typing import cast

from compas.geometry import Brep

from .geometryobject import GeometryObject as ViewerGeometryObject


class BRepObject(ViewerGeometryObject):
    """Viewer scene object for displaying COMPAS Brep geometry.

    The object consumes the stable `compas.geometry.Brep` wrapper. The active
    Brep backend provides tessellation and topology through COMPAS plugins.

    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        geometry = cast(Brep, self.geometry)
        self._viewmesh, self._boundaries = geometry.to_tesselation()

    @property
    def points(self) -> list[Iterable[float]]:
        """Boundary vertices of the Brep."""
        geometry = cast(Brep, self.geometry)
        return [point for point in geometry.points]

    @property
    def lines(self) -> list[Iterable[Iterable[float]]]:
        """Discretized boundary curves of the Brep."""
        lines: list[Iterable[Iterable[float]]] = []
        for polyline in self._boundaries:
            lines += polyline.lines
        return lines

    @property
    def viewmesh(self) -> tuple[list[Iterable[float]], list[list[int]]]:
        """Triangulated view mesh of the Brep."""
        vertices, faces = self._viewmesh.to_vertices_and_faces(triangulated=True)
        return [vertex for vertex in vertices], [face for face in faces]
