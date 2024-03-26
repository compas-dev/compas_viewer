from typing import Optional

from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GeometryObject
from compas.tolerance import TOL
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
            self._viewmesh, self._boundaries = self.geometry.to_tesselation(TOL.lineardeflection)

        @property
        def points(self) -> Optional[list[Point]]:
            """The points to be shown in the viewer."""
            return self.geometry.points

        @property
        def lines(self) -> Optional[list[Line]]:
            """The lines to be shown in the viewer."""
            lines = []
            for polyline in self._boundaries:
                for pair in pairwise(polyline.points):
                    lines.append(Line(*pair))

            return lines

        @property
        def viewmesh(self) -> Mesh:
            """The mesh volume to be shown in the viewer."""
            return self._viewmesh

except ImportError:
    pass
