from typing import Optional
from typing import Tuple

from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class PointObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Point geometry.

    Parameters
    ----------
    point : :class:`compas.geometry.Point`
        The point geometry to display.
    show_points : bool, optional
        Whether to display the point in the viewer. Default is True.

    See Also
    --------
    :class:`compas.geometry.Point`
    """

    def __init__(self, point: Point, **kwargs):
        super().__init__(geometry=point, **kwargs)
        self.show_points = True
        self.geometry: Point

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        return [self.geometry]

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        pass

    @property
    def surfaces(self) -> Optional[list[Tuple[Point, Point, Point]]]:
        """The surface to be shown in the viewer. Currently only triangles are supported."""
        pass
