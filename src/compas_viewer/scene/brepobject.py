from typing import Optional
from typing import Tuple

from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject
from compas.utilities import pairwise

from .geometryobject import GeometryObject as ViewerGeometryObject

try:
    from compas_occ.brep import OCCBrep

    class BRepObject(ViewerGeometryObject, GeometryObject):
        """Viewer scene object for displaying COMPAS OCCBrep geometry.

        Attributes
        ----------
        brep : :class:`compas_occ.brep.OCCBrep`
            The compas_occ Brep object.
        mesh : :class:`compas.datastructures.Mesh`
            The mesh representation of the Brep.

        See Also
        --------
        :class:`compas_occ.brep.Brep`
        """

        def __init__(self, brep: OCCBrep, **kwargs):
            super().__init__(geometry=brep, **kwargs)
            self.geometry: OCCBrep
            self.mesh, self.boundaries = self.geometry.to_tesselation(self.LINEARDEFLECTION)

        @property
        def points(self) -> Optional[list[Point]]:
            """The points to be shown in the viewer."""
            return self.geometry.points

        @property
        def lines(self) -> Optional[list[Line]]:
            """The lines to be shown in the viewer."""
            lines = []
            for polyline in self.boundaries:
                for pair in pairwise(polyline.points):
                    lines.append(Line(*pair))

            return lines

        @property
        def surfaces(self) -> Optional[list[Tuple[Point, Point, Point]]]:
            """The surface to be shown in the viewer. Currently only triangles are supported."""
            surface_points = []
            vertices, faces = self.mesh.to_vertices_and_faces()
            for face in faces:
                face_points = [vertices[i] for i in face]
                surface_points.append(face_points)
            return surface_points

except ImportError:
    pass
