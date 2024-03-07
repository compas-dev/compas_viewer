from math import pi
from typing import Optional
from typing import Tuple

from compas.geometry import Capsule
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class CapsuleObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Capsule geometry.

    See Also
    --------
    :class:`compas.geometry.Capsule`
    """

    def __init__(self, capsule: Capsule, **kwargs):
        super().__init__(geometry=capsule, **kwargs)
        self.geometry: Capsule
        self.u = int(2 * pi * capsule.radius / self.LINEARDEFLECTION)
        self.v = self.u

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
        vertices, faces = self.geometry.to_vertices_and_faces(self.u, self.v, True)
        for face in faces:
            face_points = [vertices[i] for i in face]
            surface_points.append(face_points)
        return surface_points
