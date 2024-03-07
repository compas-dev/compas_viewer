from math import pi
from typing import Optional
from typing import Tuple

from compas.geometry import Cylinder
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class CylinderObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Cylinder geometry.

    See Also
    --------
    :class:`compas.geometry.Cylinder`
    """

    def __init__(self, cylinder: Cylinder, **kwargs):
        super().__init__(geometry=cylinder, **kwargs)
        self.geometry: Cylinder
        self.u = int(2 * pi * cylinder.radius / self.LINEARDEFLECTION)

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        pass

    @property
    def lines(self) -> Optional[list[Line]]:
        pass

    @property
    def surfaces(self) -> Optional[list[Tuple[Point, Point, Point]]]:
        """The surface to be shown in the viewer. Currently only triangles are supported."""
        surface_points = []
        vertices, faces = self.geometry.to_vertices_and_faces(self.u, True)
        for face in faces:
            face_points = [vertices[i] for i in face]
            surface_points.append(face_points)
        return surface_points
