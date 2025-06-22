from compas.geometry import Point

from .geometryobject import GeometryObject


class PointObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Point geometry."""

    geometry: Point

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_points = True

    @property
    def points(self) -> list[Point]:
        return [self.geometry]
