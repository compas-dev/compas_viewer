from typing import cast

from compas.geometry import Surface
from compas.geometry import Tessellation

from .sceneobject import ShaderDataType
from .tessellationobject import TessellationObject


class SurfaceObject(TessellationObject):
    """Viewer scene object for displaying a parametric surface."""

    @property
    def tessellation(self) -> Tessellation:
        return cast(Surface, self.geometry).tessellation

    def _read_points_data(self) -> ShaderDataType:
        positions = cast(Surface, self.geometry).vertices
        colors = [self.pointcolor] * len(positions)
        elements = [[index] for index in range(len(positions))]
        return positions, colors, elements

    def _read_lines_data(self) -> ShaderDataType:
        geometry = cast(Surface, self.geometry)
        positions = geometry.vertices
        colors = [self.linecolor] * len(positions)
        return positions, colors, geometry.edges
