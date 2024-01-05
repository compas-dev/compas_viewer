import math

from compas.geometry import Frame

from .polylineobject import PolylineObject


class EllipseObject(PolylineObject):
    """Object for displaying COMPAS Ellipse geometry."""

    def __init__(self, ellipse, u=16, **kwargs):
        self.u = u
        self.calculate_ellipse_points(ellipse)
        super().__init__(ellipse, close=True, **kwargs)

    def calculate_ellipse_points(self, ellipse):
        frame = Frame.from_plane(ellipse.plane)
        ellipse.points = [
            frame.to_world_coordinates(
                [
                    math.cos(i * math.pi * 2 / self.u) * ellipse.major,
                    math.sin(i * math.pi * 2 / self.u) * ellipse.minor,
                    0,
                ]
            )
            for i in range(self.u)
        ]

    def update(self):
        self.calculate_ellipse_points(self._data)
        self.init()
        super().update()

    @property
    def properties(self):
        return ["u"]
