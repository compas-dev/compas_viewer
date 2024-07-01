from typing import Optional

from compas.datastructures import Mesh
from compas.geometry import Frame
from compas.geometry import Line
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
        self.frame: Frame = Frame.from_plane(self.plane)
        self.planesize = planesize

        self.vertices = [
            Point(*self.frame.to_world_coordinates([-self.planesize, -self.planesize, 0])),
            Point(*self.frame.to_world_coordinates([self.planesize, -self.planesize, 0])),
            Point(*self.frame.to_world_coordinates([self.planesize, self.planesize, 0])),
            Point(*self.frame.to_world_coordinates([-self.planesize, self.planesize, 0])),
        ]

    @property
    def plane(self) -> Plane:
        return self.item

    @property
    def points(self) -> Optional[list[Point]]:
        return None

    @property
    def lines(self) -> Optional[list[Line]]:
        return [
            Line(
                Point(*self.frame.to_world_coordinates([0, 0, 0])),
                Point(*self.frame.to_world_coordinates([0, 0, self.planesize])),
            )
        ]

    @property
    def viewmesh(self) -> Mesh:
        return Mesh.from_vertices_and_faces(self.vertices, [[0, 1, 2], [0, 2, 3]])
