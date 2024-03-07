from math import cos
from math import pi
from math import sin
from math import sqrt
from typing import Optional
from typing import Tuple

from compas.geometry import Ellipse
from compas.geometry import Frame
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class EllipseObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Ellipse geometry.

    Parameters
    ----------
    ellipse : :class:`compas.geometry.Ellipse`
        A COMPAS ellipse geometry.
    **kwargs : dict, optional
        Additional options for the :class:`compas_viewer.scene.ViewerSceneObject`
        and :class:`compas.scene.GeometryObject`.

    See Also
    --------
    :class:`compas.geometry.Ellipse`
    """

    def __init__(self, ellipse: Ellipse, **kwargs):
        super().__init__(geometry=ellipse, **kwargs)
        self.geometry: Ellipse
        self.u = int(self._proximate_circumference() / self.LINEARDEFLECTION)
        self.show_lines = True

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        return [self.geometry.plane.point]

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        frame = Frame.from_plane(self.geometry.plane)
        line_points = [
            frame.to_world_coordinates(
                Point(
                    cos(i * pi * 2 / self.u) * self.geometry.major,
                    sin(i * pi * 2 / self.u) * self.geometry.minor,
                    0,
                )
            )
            for i in range(self.u)
        ]
        return [Line(line_points[i - 1], line_points[i]) for i in range(0, self.u)]

    @property
    def surfaces(self) -> Optional[list[Tuple[Point, Point, Point]]]:
        """The surface to be shown in the viewer. Currently only triangles are supported."""
        return []

    def _proximate_circumference(self):
        return 2 * pi * sqrt((self.geometry.major**2 + self.geometry.minor**2) / 2)
