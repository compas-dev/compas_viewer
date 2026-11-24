from collections.abc import Iterable
from collections.abc import Sequence
from typing import Any
from typing import cast

from compas.colors import Color
from compas.itertools import flatten
from compas.typing import RealInput
from compas.typing import VerticesFaces

from .sceneobject import BufferValues
from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject


class GeometryObject(ViewerSceneObject):
    """Viewer scene object for displaying COMPAS Geometry.

    Parameters
    ----------
    geometry
        A COMPAS geometry.
    u
        The number of cells in the u-direction of structured geometry.
    v
        The number of cells in the v-direction of structured geometry.
    pointcolor
        The color of the points.
    linecolor
        The color of the lines.
    surfacecolor
        The color of the surfaces.
    **kwargs
        Additional scene-object options.

    """

    @property
    def facecolor(self) -> Color:
        return cast(Color, self.surfacecolor)

    @facecolor.setter
    def facecolor(self, color: Color) -> None:
        self.surfacecolor = color

    @property
    def points(self) -> Sequence[Iterable[RealInput]] | None:
        return None

    @property
    def lines(self) -> Sequence[Iterable[Iterable[RealInput]]] | None:
        return None

    @property
    def viewmesh(self) -> VerticesFaces | None:
        return None

    def _read_points_data(self) -> ShaderDataType:
        if self.points is None:
            return [], [], []
        positions = self.points
        colors = [self.pointcolor] * len(positions)
        elements = [[i] for i in range(len(positions))]
        return positions, colors, elements

    def _read_lines_data(self) -> ShaderDataType:
        if self.lines is None:
            return [], [], []
        positions = []
        elements = []
        positions = list(flatten(self.lines))
        colors = [self.linecolor] * len(positions)
        elements = [[2 * i, 2 * i + 1] for i in range(len(self.lines))]
        return positions, colors, elements

    def _read_frontfaces_data(self) -> ShaderDataType:
        if self.viewmesh is None:
            return [], [], []
        positions, elements = self.viewmesh
        colors = [self.facecolor] * len(positions)
        return cast(BufferValues, positions), colors, cast(BufferValues, elements)

    def _read_backfaces_data(self) -> ShaderDataType:
        if self.viewmesh is None:
            return [], [], []
        positions, source_elements = self.viewmesh
        elements = [list(reversed(element)) for element in source_elements]
        colors = [self.facecolor] * len(positions)
        return cast(BufferValues, positions), colors, elements

    def _rebuild_resolution_buffers(self) -> None:
        """Refresh and rebuild active renderer buffers after resolution changes."""
        if self.viewer.running and self.sceneobject in self.runtime_scene.objects:
            self.refresh_data()
            self.viewer.renderer.rebuild_buffers()
            self.viewer.renderer.update()

    def __init__(self, u: int = 16, v: int = 16, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not hasattr(self.sceneobject, "u"):
            object.__setattr__(self, "u", u)
        if not hasattr(self.sceneobject, "v"):
            object.__setattr__(self, "v", v)
