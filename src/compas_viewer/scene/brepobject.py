from typing import List
from typing import Optional
from typing import Tuple

from compas.colors import Color
from compas.geometry import Point
from compas.geometry import Polyline
from compas.utilities import pairwise

from .meshobject import MeshObject

try:
    from compas_occ.brep import BRep

    class BRepObject(MeshObject):
        """Viewer scene object for displaying COMPAS :class:`compas_occ.brep.Brep` geometry.

        Attributes
        ----------
        brep : :class:`compas_occ.brep.BRep`
            The compas_occ Brep object.
        mesh : :class:`compas.datastructures.Mesh`
            The tesselation mesh representation of the Brep.
        """

        def __init__(self, brep: BRep, **kwargs):
            self.brep = brep
            mesh, boundaries = self.to_viewmesh()
            super().__init__(mesh=mesh, **kwargs)
            self.boundaries = boundaries

        def _read_lines_data(self) -> Optional[Tuple[List[Point], List[Color], List[List[int]]]]:
            positions = []
            colors = []
            elements = []
            lines = []
            for polyline in self.boundaries:
                lines += pairwise(polyline.points)
            count = 0
            for i, (pt1, pt2) in enumerate(lines):
                positions.append(pt1)
                positions.append(pt2)
                color = self.linescolor.get(i, self.linescolor["_default"])  # type: ignore
                colors.append(color)
                colors.append(color)
                elements.append([count, count + 1])
                count += 2
            return positions, colors, elements

        def to_viewmesh(self, linear_deflection=1):
            """
            Convert the BRep to a view mesh.
            """
            lines = []
            for edge in self.brep.edges:
                if edge.is_line:
                    lines.append(Polyline([edge.vertices[0].point, edge.vertices[-1].point]))
            return self.brep.to_tesselation(linear_deflection=linear_deflection), lines

except ImportError:
    pass
