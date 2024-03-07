from typing import Optional
from typing import Tuple

from compas.geometry import Line
from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class NurbsSurfaceObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS NurbsSurface geometry.

    See Also
    --------
    :class:`compas.geometry.NurbsSurface`
    """

    def __init__(self, surface: NurbsSurface, **kwargs):
        super().__init__(geometry=surface, **kwargs)
        self.geometry: NurbsSurface

        # LINEARDEFLECTION not implemented in NurbsSurface.
        self.u = int(16 + (0 * self.LINEARDEFLECTION))
        self.v = int(16 + (0 * self.LINEARDEFLECTION))

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        points = []
        for row in self.geometry.points:
            points.extend(row)
        return points

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        lines = []
        for row in self.geometry.points:
            for i in range(len(row) - 1):
                lines.append(Line(row[i], row[i + 1]))
        for col in zip(*self.geometry.points):
            for i in range(len(col) - 1):
                lines.append(Line(col[i], col[i + 1]))
        return lines

    @property
    def surfaces(self) -> Optional[list[Tuple[Point, Point, Point]]]:
        """The surface to be shown in the viewer. Currently only triangles are supported."""
        surface_points = []
        for triangle in self.geometry.to_triangles(nu=self.u, nv=self.v):
            surface_points.append(triangle)
        return surface_points
