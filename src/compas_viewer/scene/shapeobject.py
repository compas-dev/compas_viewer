from typing import Any
from typing import cast

from compas.colors import Color
from compas.geometry import Shape
from compas.geometry import Tessellation

from .sceneobject import ShaderDataType
from .tessellationobject import TessellationObject


class ShapeObject(TessellationObject):
    """Viewer scene object for displaying COMPAS Geometry.

    Parameters
    ----------
    geometry : :class:`compas.geometry.Geometry`
        A COMPAS geometry.
    v : int, optional
        The number of vertices in the u-direction of non-OCC geometries.
    u : int, optional
        The number of vertices in the v-direction of non-OCC geometries.
    pointcolor : :class:`compas.colors.Color`, optional
        The color of the points. Default is the value of `pointcolor` in `viewer.config`.
    linecolor : :class:`compas.colors.Color`, optional
        The color of the lines. Default is the value of `linecolor` in `viewer.config`.
    surfacecolor : :class:`compas.colors.Color`, optional
        The color of the surfaces. Default is the value of `surfacecolor` in `viewer.config`.
    **kwargs : dict, optional
        Additional options for the :class:`compas_viewer.scene.ViewerSceneObject`
        and :class:`compas.scene.GeometryObject`.

    Attributes
    ----------
    geometry : :class:`compas.geometry.Geometry`
        The COMPAS geometry.
    pointcolor : :class:`compas.colors.Color`
        The color of the points.
    linecolor : :class:`compas.colors.Color`
        The color of the lines.
    surfacecolor : :class:`compas.colors.Color`
        The color of the surfaces.
    mesh : :class:`compas.datastructures.Mesh`
        The triangulated mesh representation of the geometry.
    LINEARDEFLECTION : float
        The default linear deflection for the geometry.

    See Also
    --------
    :class:`compas.geometry.Geometry`

    """

    def __init__(self, u: int | None = None, v: int | None = None, **kwargs: Any) -> None:
        geometry = cast(Shape, kwargs.get("geometry", kwargs.get("item")))
        super().__init__(
            u=geometry.resolution_u if u is None else u,
            v=geometry.resolution_v if v is None else v,
            **kwargs,
        )

    @property
    def u(self) -> int:
        return cast(Shape, self.geometry).resolution_u

    @u.setter
    def u(self, u: int) -> None:
        cast(Shape, self.geometry).resolution_u = u
        self._rebuild_buffers()

    @property
    def v(self) -> int:
        return cast(Shape, self.geometry).resolution_v

    @v.setter
    def v(self, v: int) -> None:
        cast(Shape, self.geometry).resolution_v = v
        self._rebuild_buffers()

    def _rebuild_buffers(self) -> None:
        if self.viewer.running and self in self.viewer.scene.objects:
            self.viewer.renderer.rebuild_buffers()
            self.viewer.renderer.update()

    @property
    def facecolor(self) -> Color:
        return self.surfacecolor

    @facecolor.setter
    def facecolor(self, color: Color) -> None:
        self.surfacecolor = color

    @property
    def tessellation(self) -> Tessellation:
        return cast(Shape, self.geometry).tessellation

    def _read_points_data(self) -> ShaderDataType:
        positions = cast(Shape, self.geometry).vertices
        colors = [self.pointcolor] * len(positions)
        elements = [[i] for i in range(len(positions))]
        return positions, colors, elements

    def _read_lines_data(self) -> ShaderDataType:
        geometry = cast(Shape, self.geometry)
        vertices = geometry.vertices
        edges = geometry.edges
        positions = [vertices[vertex] for edge in edges for vertex in edge]
        colors = [self.linecolor] * len(positions)
        elements = [[2 * i, 2 * i + 1] for i in range(len(edges))]
        return positions, colors, elements
