from collections.abc import Iterable
from collections.abc import Sequence
from typing import Any
from typing import cast

from compas.colors import Color
from compas.itertools import flatten
from compas.scene import GeometryObject as BaseGeometryObject
from compas.scene.descriptors.color import ColorAttribute

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject


class GeometryObject(ViewerSceneObject, BaseGeometryObject):
    """Viewer scene object for displaying COMPAS Geometry.

    Parameters
    ----------
    geometry
        A COMPAS geometry.
    v
        The number of vertices in the u-direction of non-OCC geometries.
    u
        The number of vertices in the v-direction of non-OCC geometries.
    pointcolor
        The color of the points. Default is the value of `pointcolor` in `viewer.config`.
    linecolor
        The color of the lines. Default is the value of `linecolor` in `viewer.config`.
    surfacecolor
        The color of the surfaces. Default is the value of `surfacecolor` in `viewer.config`.
    **kwargs
        Additional scene-object options.

    """

    pointcolor = ColorAttribute(default=Color(0.2, 0.2, 0.2))
    linecolor = ColorAttribute(default=Color(0.2, 0.2, 0.2))
    surfacecolor = ColorAttribute(default=Color(0.9, 0.9, 0.9))

    def __init__(self, u: int | None = 16, v: int | None = 16, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.u = 16 if u is None else u
        self.v = 16 if v is None else v

    @property
    def facecolor(self) -> Color:
        return cast(Color, self.surfacecolor)

    @facecolor.setter
    def facecolor(self, color: Color) -> None:
        self.surfacecolor = color

    @property
    def points(self) -> Sequence[Iterable[float]] | None:
        return None

    @property
    def lines(self) -> Sequence[Iterable[Iterable[float]]] | None:
        return None

    @property
    def viewmesh(self) -> tuple[Sequence[Iterable[float]], Sequence[Sequence[int]]] | None:
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
        return positions, colors, elements

    def _read_backfaces_data(self) -> ShaderDataType:
        if self.viewmesh is None:
            return [], [], []
        positions, source_elements = self.viewmesh
        elements = [list(reversed(element)) for element in source_elements]
        colors = [self.facecolor] * len(positions)
        return positions, colors, elements
