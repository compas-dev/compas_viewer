from typing import Optional
from typing import Tuple

from compas.colors import Color
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
    pointcolor : :class:`compas.colors.Color`, optional
        The color of the points. Global settings in the viewer will be used if not specified.
    linecolor : :class:`compas.colors.Color`, optional
        The color of the lines. Global settings in the viewer will be used if not specified.
    surfacecolor : :class:`compas.colors.Color`, optional
        The color of the surfaces. Global settings in the viewer will be used if not specified.
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

    LINEARDEFLECTION = 0.2

    def __init__(
        self,
        geometry: Geometry,
        pointcolor: Optional[Color] = None,
        linecolor: Optional[Color] = None,
        surfacecolor: Optional[Color] = None,
        **kwargs
    ):

        super().__init__(geometry=geometry, **kwargs)
        self.geometry: Geometry

        self.pointcolor = pointcolor or self.viewer.config.pointscolor
        self.linecolor = linecolor or self.viewer.config.linescolor
        self.surfacecolor = surfacecolor or self.viewer.config.facescolor

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        raise NotImplementedError

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        raise NotImplementedError

    @property
    def surfaces(self) -> Optional[list[Tuple[Point, Point, Point]]]:
        """The surface to be shown in the viewer. Currently only triangles are supported."""
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
        if self.surfaces is None:
            return [], [], []
        positions = []
        for surface in self.surfaces:
            positions.extend(surface)
        colors = [self.surfacecolor] * 3 * len(positions)
        elements = [[3 * i, 3 * i + 1, 3 * i + 2] for i in range(len(positions))]

        return positions, colors, elements

    def _read_backfaces_data(self) -> ShaderDataType:
        if self.surfaces is None:
            return [], [], []
        positions = []
        for surface in self.surfaces:
            positions.extend(surface[::-1])
        colors = [self.surfacecolor] * 3 * len(positions)
        elements = [[3 * i, 3 * i + 1, 3 * i + 2] for i in range(len(positions))]

        return positions, colors, elements
