from compas.geometry import Frame
from compas.geometry import Plane
from compas.geometry import Point

from .geometryobject import GeometryObject


class PlaneObject(GeometryObject):
    """
    Viewer scene object for displaying COMPAS Plane geometry.

    Parameters
    ----------
    planesize : float
        The size of the plane.
        Default is 1.

    See Also
    --------
    :class:`compas.geometry.Plane`
    """

    def __init__(self, planesize: float = 1, **kwargs):
        super().__init__(**kwargs)
        self.planesize = planesize

    @property
    def plane(self) -> Plane:
        return self.item

    @property
    def points(self) -> list[Point]:
        return [self.plane.point]

    @property
    def lines(self) -> list[list[Point]]:
        frame = Frame.from_plane(self.plane)
        return [[frame.to_world_coordinates([0, 0, 0]), frame.to_world_coordinates([0, 0, self.planesize])]]

    @property
    def viewmesh(self) -> tuple[list[Point], list[list[int]]]:
        frame = Frame.from_plane(self.plane)
        vertices = [
            frame.to_world_coordinates([-self.planesize, -self.planesize, 0]),
            frame.to_world_coordinates([self.planesize, -self.planesize, 0]),
            frame.to_world_coordinates([self.planesize, self.planesize, 0]),
            frame.to_world_coordinates([-self.planesize, self.planesize, 0]),
        ]
        return vertices, [[0, 1, 2], [0, 2, 3]]
