from typing import cast

from compas.geometry import PolygonalSurface
from compas.geometry import Tessellation

from .sceneobject import ShaderDataType
from .tessellationobject import TessellationObject


class PolygonalSurfaceObject(TessellationObject):
    """Viewer scene object for displaying a polygonal surface."""

    @property
    def tessellation(self) -> Tessellation:
        return cast(PolygonalSurface, self.geometry).tessellation

    def _read_points_data(self) -> ShaderDataType:
        positions = cast(PolygonalSurface, self.geometry).vertices
        colors = [self.pointcolor] * len(positions)
        elements = [[index] for index in range(len(positions))]
        return positions, colors, elements

    def _read_lines_data(self) -> ShaderDataType:
        geometry = cast(PolygonalSurface, self.geometry)
        vertices = geometry.vertices
        edges = geometry.edges
        positions = vertices
        colors = [self.linecolor] * len(positions)
        return positions, colors, edges
