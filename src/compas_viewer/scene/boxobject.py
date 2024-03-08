from typing import Optional

from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class BoxObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Box geometry.

    See Also
    --------
    :class:`compas.geometry.Box`
    """

    def __init__(self, box: Box, **kwargs):
        super().__init__(geometry=box, **kwargs)
        self.geometry: Box

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        return self.geometry.to_vertices_and_faces()[0]

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        return [
            Line(self.geometry.corner(i), self.geometry.corner(j))
            for i, j in [
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 0),
                (4, 5),
                (5, 6),
                (6, 7),
                (7, 4),
                (0, 4),
                (1, 5),
                (2, 6),
                (3, 7),
            ]
        ]

    @property
    def viewmesh(self):
        """The mesh volume to be shown in the viewer."""
        return Mesh.from_shape(self.geometry, triangulated=True)
