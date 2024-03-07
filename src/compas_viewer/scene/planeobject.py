from typing import Optional
from typing import Tuple

from compas.geometry import Frame
from compas.geometry import Line
from compas.geometry import Plane
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class PlaneObject(ViewerGeometryObject, GeometryObject):
    """
    Viewer scene object for displaying COMPAS Plane geometry.

    Parameters
    ----------
    plane : :class:`compas.geometry.Plane`
        The plane geometry.
    planesize : float
        The size of the plane.
        Default is 1.

    See Also
    --------
    :class:`compas.geometry.Plane`
    """

    def __init__(self, plane: Plane, planesize: float = 1, **kwargs):
        super().__init__(geometry=plane, **kwargs)
        self.frame = Frame.from_plane(plane)
        self.planesize = planesize

        self.vertices = [
            Point(*self.frame.to_world_coordinates([-self.planesize, -self.planesize, 0])),
            Point(*self.frame.to_world_coordinates([self.planesize, -self.planesize, 0])),
            Point(*self.frame.to_world_coordinates([self.planesize, self.planesize, 0])),
            Point(*self.frame.to_world_coordinates([-self.planesize, self.planesize, 0])),
        ]

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        pass

    @property
    def lines(self) -> Optional[list[Line]]:
        return [
            Line(
                Point(*self.frame.to_world_coordinates([0, 0, 0])),
                Point(*self.frame.to_world_coordinates([0, 0, self.planesize])),
            )
        ]

    @property
    def surfaces(self) -> Optional[list[Tuple[Point, Point, Point]]]:
        """The surface to be shown in the viewer. Currently only triangles are supported."""
        return [
            (self.vertices[0], self.vertices[1], self.vertices[2]),
            (self.vertices[0], self.vertices[2], self.vertices[3]),
        ]
