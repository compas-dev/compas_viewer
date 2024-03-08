from typing import Optional
from typing import Tuple

from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class LineObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Line geometry.

    See Also
    --------
    :class:`compas.geometry.Line`
    """

    def __init__(self, line: Line, **kwargs):
        super().__init__(geometry=line, **kwargs)
        self.geometry: Line
        self.show_lines = True

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        return [self.geometry.start, self.geometry.end]

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        return [self.geometry]

    @property
    def viewmesh(self):
        """The mesh volume to be shown in the viewer."""
        return None
