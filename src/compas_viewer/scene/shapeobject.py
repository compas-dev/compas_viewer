from typing import Any
from typing import cast

from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Capsule
from compas.geometry import Cone
from compas.geometry import Cylinder
from compas.geometry import PolygonalSurface
from compas.geometry import Shape
from compas.geometry import Sphere
from compas.geometry import Tessellation
from compas.geometry import Torus

from .sceneobject import ShaderDataType
from .tessellationobject import TessellationObject


class ShapeObject(TessellationObject):
    """Viewer scene object for displaying a structured COMPAS shape.

    Parameters
    ----------
    geometry
        The structured shape.
    u
        The scene-owned cell count in the u-direction.
    v
        The scene-owned cell count in the v-direction.
    pointcolor
        The point color.
    linecolor
        The line color.
    surfacecolor
        The surface color.
    **kwargs
        Additional scene-object options.

    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @property
    def facecolor(self) -> Color:
        return self.surfacecolor

    @facecolor.setter
    def facecolor(self, color: Color) -> None:
        self.surfacecolor = color

    @property
    def tessellation(self) -> Tessellation:
        """A fresh triangulation at the scene object's resolution."""
        return self._polygonal_surface().triangulated()

    def _read_points_data(self) -> ShaderDataType:
        positions = self._polygonal_surface().vertices
        colors = [self.pointcolor] * len(positions)
        elements = [[i] for i in range(len(positions))]
        return positions, colors, elements

    def _read_lines_data(self) -> ShaderDataType:
        surface = self._polygonal_surface()
        vertices = surface.vertices
        edges = surface.edges
        positions = [vertices[vertex] for edge in edges for vertex in edge]
        colors = [self.linecolor] * len(positions)
        elements = [[2 * i, 2 * i + 1] for i in range(len(edges))]
        return positions, colors, elements

    def _polygonal_surface(self) -> PolygonalSurface:
        """Create a fresh polygonal representation for the concrete producer."""
        geometry = cast(Shape, self.geometry)
        if isinstance(geometry, Box):
            return geometry.to_polygonal_surface()
        if isinstance(geometry, (Cone, Cylinder)):
            return geometry.to_polygonal_surface(nu=self.u)
        if isinstance(geometry, (Capsule, Sphere, Torus)):
            return geometry.to_polygonal_surface(nu=self.u, nv=self.v)
        return geometry.to_polygonal_surface()
