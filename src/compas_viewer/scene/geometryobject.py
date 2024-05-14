from typing import Optional

from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Geometry
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject as BaseGeometryObject

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

    def __init__(
        self,
        geometry: Geometry,
        u: Optional[int] = 16,
        v: Optional[int] = 16,
        facecolor: Optional[Color] = None,
        **kwargs,
    ):
        super().__init__(geometry=geometry, **kwargs)
        self.geometry: Geometry

        self.u = u
        self.v = v
        self.facecolor = facecolor or Color(0.9, 0.9, 0.9)

    @property
    def facecolor(self) -> Color:
        """The color of the faces."""
        return self.surfacecolor

    @facecolor.setter
    def facecolor(self, color: Color) -> None:
        self.surfacecolor = color

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        raise NotImplementedError

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        raise NotImplementedError

    @property
    def viewmesh(self) -> Mesh:
        """The mesh volume to be shown in the viewer."""
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
        for line in self.lines:
            positions.append(line.start)
            positions.append(line.end)
        colors = [self.linecolor] * 2 * len(positions)
        elements = [[2 * i, 2 * i + 1] for i in range(len(positions))]

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
