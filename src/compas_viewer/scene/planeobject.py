from typing import List
from typing import Optional
from typing import Tuple

from compas.colors import Color
from compas.geometry import Frame
from compas.geometry import Plane
from compas.geometry import Point
from compas.scene import GeometryObject

from .sceneobject import ViewerSceneObject


class PlaneObject(ViewerSceneObject, GeometryObject):
    """
    The scene object of the :class:`compas.geometry.Plane` geometry.

    Parameters
    ----------
    plane : :class:`compas.geometry.Plane`
        The plane geometry.
    planesize : float
        The size of the plane.
        Default is 1.
    """

    def __init__(self, plane: Plane, planesize: float = 1, **kwargs):
        super(PlaneObject, self).__init__(geometry=plane, **kwargs)
        self.frame = Frame.from_plane(plane)
        self.planesize = planesize

        self.vertices = [
            Point(*self.frame.to_world_coordinates([-self.planesize, -self.planesize, 0])),
            Point(*self.frame.to_world_coordinates([self.planesize, -self.planesize, 0])),
            Point(*self.frame.to_world_coordinates([self.planesize, self.planesize, 0])),
            Point(*self.frame.to_world_coordinates([-self.planesize, self.planesize, 0])),
        ]

    def _read_lines_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        positions = [
            Point(*self.frame.to_world_coordinates([0, 0, 0])),
            Point(*self.frame.to_world_coordinates([0, 0, self.planesize])),
        ]
        colors = [self.linescolor["_default"], self.linescolor["_default"]]
        elements = [[0, 1]]

        return positions, colors, elements

    def _read_points_data(self):
        """No points data exist for this geometry, Return None."""
        return None

    def _read_frontfaces_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        return self.vertices, [self.facescolor["_default"]] * 4, [[0, 1, 2], [0, 2, 3]]

    def _read_backfaces_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
        return self.vertices, [self.facescolor["_default"]] * 4, [[2, 1, 0], [3, 2, 0]]
