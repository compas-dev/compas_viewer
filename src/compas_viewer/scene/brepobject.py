from compas.geometry import Polyline
from compas.utilities import pairwise

from .meshobject import MeshObject
from .sceneobject import DataType

try:
    from compas_occ.brep import OCCBrep

    class BRepObject(MeshObject):
        """Viewer scene object for displaying COMPAS OCCBrep geometry.

        Attributes
        ----------
        brep : :class:`compas_occ.brep.OCCBrep`
            The compas_occ Brep object.
        mesh : :class:`compas.datastructures.Mesh`
            The tesselation mesh representation of the Brep.

        See Also
        --------
        :class:`compas_occ.brep.Brep`
        """

        def __init__(self, brep: OCCBrep, **kwargs):
            self.brep = brep
            mesh, boundaries = self.to_viewmesh()
            super().__init__(mesh=mesh, **kwargs)
            self.boundaries = boundaries

        def _read_lines_data(self) -> DataType:
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
            Convert the OCCBrep to a view mesh.
            """
            lines = []
            for edge in self.brep.edges:
                if edge.is_line:
                    lines.append(Polyline([edge.vertices[0].point, edge.vertices[-1].point]))
            return self.brep.to_tesselation(linear_deflection=linear_deflection), lines

except ImportError:
    pass
