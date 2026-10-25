from typing import cast

from compas.geometry import Line
from compas.geometry import Point

from .geometryobject import GeometryObject


class LineObject(GeometryObject):
    """Viewer scene object for displaying COMPAS Line geometry."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.show_lines = True

    @property
    def points(self) -> list[Point] | None:
        line = cast(Line, self.geometry)
        return [line.start, line.end]

    @property
    def lines(self) -> list[Line] | None:
        return [cast(Line, self.geometry)]
