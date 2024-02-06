from compas.datastructures import Mesh
from compas.utilities import pairwise

from .geometryobject import GeometryObject
from .sceneobject import DataType

import numpy as np

try:
    from compas_occ.brep import OCCBrep

    class BRepObject(GeometryObject):
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

        def __init__(self, brep: OCCBrep, facecolors=None, shellcolors=None, **kwargs):
            self.brep = brep
            self.boundaries = []
            self.mesh = Mesh()
            self.facecolors = facecolors
            shells = brep.shells or [brep]

            # TODO: it is not facecolors, it is verexcolor
            if shellcolors is not None:
                self.facecolors = []

            for i_shell, shell in enumerate(shells):
                mesh, boundaries = shell.to_tesselation(kwargs.get("linear_deflection ", self.LINEARDEFLECTION))
                mesh.quads_to_triangles()
                if shellcolors is not None:
                    for _ in range(mesh.number_of_faces()):
                        self.facecolors.append(shellcolors[i_shell])
                        self.facecolors.append(shellcolors[i_shell])
                        self.facecolors.append(shellcolors[i_shell])
                self.mesh.join(mesh)
                self.boundaries += boundaries

            if not self.facecolors:
                self.facecolors = [[0.5, 0.5, 0.5, 1.0] for _ in range(self.mesh.number_of_faces() * 3)]


            super().__init__(brep, mesh=self.mesh, doublesided=True, **kwargs)

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

        def _read_frontfaces_data(self):
            vertices, faces = self.mesh.to_vertices_and_faces()
            vertices = np.array(vertices)
            faces = np.array(faces)
            positions = vertices[faces].reshape(-1, 3).tolist()
            elements = np.arange(len(positions) * 3).reshape(-1, 3).tolist()
            colors = [color[:3] for color in self.facecolors]

            if self.use_rgba:
                opacities = [color[3] for color in self.facecolors]
                return positions, colors, opacities, elements
            else:
                return positions, colors, elements

        def _read_backfaces_data(self):
            vertices, faces = self.mesh.to_vertices_and_faces()
            vertices = np.array(vertices)
            faces = np.array(faces)
            faces = faces[:, ::-1]
            positions = vertices[faces].reshape(-1, 3).tolist()
            elements = np.arange(len(positions) * 3).reshape(-1, 3).tolist()
            colors = [color[:3] for color in self.facecolors]

            if self.use_rgba:
                opacities = [color[3] for color in self.facecolors]
                return positions, colors, opacities, elements
            else:
                return positions, colors, elements


except ImportError:
    pass
