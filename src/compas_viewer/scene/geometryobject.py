from typing import Optional

from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Geometry
from compas.geometry import Line
from compas.geometry import Point
from compas.itertools import flatten
from compas.scene import GeometryObject as BaseGeometryObject
from compas.scene.descriptors.color import ColorAttribute

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject


class GeometryObject(ViewerSceneObject, BaseGeometryObject):
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

    pointcolor = ColorAttribute(default=Color(0.2, 0.2, 0.2))
    linecolor = ColorAttribute(default=Color(0.2, 0.2, 0.2))
    surfacecolor = ColorAttribute(default=Color(0.9, 0.9, 0.9))

    def __init__(
        self,
        geometry: Geometry,
        u: Optional[int] = 16,
        v: Optional[int] = 16,
        **kwargs,
    ):
        super().__init__(geometry=geometry, **kwargs)
        self.geometry: Geometry
        self.u = u
        self.v = v

    @property
    def facecolor(self) -> Color:
        return self.surfacecolor

    @facecolor.setter
    def facecolor(self, color: Color) -> None:
        self.surfacecolor = color

    @property
    def points(self) -> Optional[list[Point]]:
        raise NotImplementedError

    @property
    def lines(self) -> Optional[list[Line]]:
        raise NotImplementedError

    @property
    def viewmesh(self) -> Mesh:
        raise NotImplementedError

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
        colors = [self.linecolor] * 2 * len(positions)
        elements = [[2 * i, 2 * i + 1] for i in range(len(self.lines))]
        return positions, colors, elements

    def _read_frontfaces_data(self) -> ShaderDataType:
        if self.viewmesh is None:
            return [], [], []
        positions, elements = self.viewmesh.to_vertices_and_faces()
        colors = [self.facecolor] * 3 * len(positions)
        return positions, colors, elements  # type: ignore

    def _read_backfaces_data(self) -> ShaderDataType:
        if self.viewmesh is None:
            return [], [], []
        positions, elements = self.viewmesh.to_vertices_and_faces()
        for element in elements:
            element.reverse()
        colors = [self.facecolor] * 3 * len(positions)
        return positions, colors, elements  # type: ignore
