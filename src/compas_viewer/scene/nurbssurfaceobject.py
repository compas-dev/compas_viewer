from typing import Optional

from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class NurbsSurfaceObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS NurbsSurface geometry.

    See Also
    --------
    :class:`compas.geometry.NurbsSurface`
    """

    def __init__(self, surface: NurbsSurface, **kwargs):
        super().__init__(geometry=surface, **kwargs)
        self.geometry: NurbsSurface

        # LINEARDEFLECTION not implemented in NurbsSurface.
        self.nu = int(16 + (0 * self.LINEARDEFLECTION))
        self.nv = int(16 + (0 * self.LINEARDEFLECTION))

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        points = []
        for row in self.geometry.points:
            points.extend(row)
        return points

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        lines = []
        for row in self.geometry.points:
            for i in range(len(row) - 1):
                lines.append(Line(row[i], row[i + 1]))
        for col in zip(*self.geometry.points):
            for i in range(len(col) - 1):
                lines.append(Line(col[i], col[i + 1]))
        return lines

    @property
    def viewmesh(self) -> Mesh:
        """The mesh volume to be shown in the viewer."""
        vertices = []
        faces = []
        for n, triangle in enumerate(self.geometry.to_triangles(nu=self.nu, nv=self.nv)):
            vertices.extend([point for point in triangle])
            faces.append([3 * n, 3 * n + 1, 3 * n + 2])
        return Mesh.from_vertices_and_faces(vertices, faces)
