from typing import Optional

from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Polyhedron
from compas.scene import GeometryObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class PolyhedronObject(ViewerGeometryObject, GeometryObject):
    """Viewer scene object for displaying COMPAS Polyhedron geometry.

    See Also
    --------
    :class:`compas.geometry.Polyhedron`
    """

    def __init__(self, polyhedron: Polyhedron, **kwargs):
        super().__init__(geometry=polyhedron, **kwargs)
        self.geometry: Polyhedron

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        return self.geometry.points

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        return self.geometry.lines

    @property
    def viewmesh(self):
        """The mesh volume to be shown in the viewer."""
        mesh = self.geometry.to_mesh()
        vertices, faces = mesh.to_vertices_and_faces(triangulated=True)
        return Mesh.from_vertices_and_faces(vertices, faces)
