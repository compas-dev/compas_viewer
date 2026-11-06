from typing import cast

from compas.geometry import Surface
from compas.geometry import Tessellation

from .sceneobject import ShaderDataType
from .tessellationobject import TessellationObject


class SurfaceObject(TessellationObject):
    """Viewer scene object for displaying a parametric surface."""

    @property
    def tessellation(self) -> Tessellation:
        """A fresh tessellation at the scene object's resolution."""
        return cast(Surface, self.geometry).to_tessellation(nu=self.u, nv=self.v)

    def _read_points_data(self) -> ShaderDataType:
        positions = cast(Surface, self.geometry).to_polygonal_surface(nu=self.u, nv=self.v).vertices
        colors = [self.pointcolor] * len(positions)
        elements = [[index] for index in range(len(positions))]
        return positions, colors, elements

    def _read_lines_data(self) -> ShaderDataType:
        polygonal_surface = cast(Surface, self.geometry).to_polygonal_surface(nu=self.u, nv=self.v)
        positions = polygonal_surface.vertices
        colors = [self.linecolor] * len(positions)
        return positions, colors, polygonal_surface.edges
