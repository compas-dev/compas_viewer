from math import pi
from typing import Optional
from typing import Tuple

from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Sphere
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class SphereObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Sphere geometry.

    See Also
    --------
    :class:`compas.geometry.Sphere`
    """

    def __init__(self, sphere: Sphere, **kwargs):
        super().__init__(geometry=sphere, **kwargs)
        self.geometry: Sphere
        self.u = int(2 * pi * sphere.radius / self.LINEARDEFLECTION)
        self.v = self.u

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        pass

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        pass

    @property
    def surfaces(self) -> Optional[list[Tuple[Point, Point, Point]]]:
        """The surface to be shown in the viewer. Currently only triangles are supported."""
        surface_points = []
        vertices, faces = self.geometry.to_vertices_and_faces(self.u, self.v, True)
        for face in faces:
            face_points = [vertices[i] for i in face]
            surface_points.append(face_points)
        return surface_points
