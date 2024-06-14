from typing import Optional

from compas.datastructures import Mesh
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
        self.frame: Frame = Frame.from_plane(plane)
        self.planesize = planesize

        self.vertices = [
            Point(*self.frame.to_world_coordinates([-self.planesize, -self.planesize, 0])),
            Point(*self.frame.to_world_coordinates([self.planesize, -self.planesize, 0])),
            Point(*self.frame.to_world_coordinates([self.planesize, self.planesize, 0])),
            Point(*self.frame.to_world_coordinates([-self.planesize, self.planesize, 0])),
        ]

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
