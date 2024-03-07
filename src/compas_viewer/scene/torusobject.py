from math import pi
from typing import Optional
from typing import Tuple

from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Torus
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class TorusObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Torus geometry.

    See Also
    --------
    :class:`compas.geometry.Torus`
    """

    def __init__(self, torus: Torus, **kwargs):
        super().__init__(geometry=torus, **kwargs)
        self.geometry: Torus
        self.u = int(2 * pi * torus.radius_axis / self.LINEARDEFLECTION)
        self.v = int(2 * pi * torus.radius_pipe / self.LINEARDEFLECTION)

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        return [self.geometry.plane.point]

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
