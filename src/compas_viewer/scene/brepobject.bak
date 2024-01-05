from compas.utilities import pairwise
from compas.geometry import centroid_points
from .bufferobject import BufferObject
from compas_occ.brep import BRep


class BRepObject(BufferObject):
    """Object for displaying compas_occ Brep.

    Attributes
    ----------
    brep : :class:`compas_occ.brep.BRep`
        The compas_occ Brep object.
    mesh : :class:`compas.datastructures.Mesh`
        The tesselation mesh representation of the Brep.
    """

    def __init__(self, brep: BRep, **kwargs):
        super().__init__(brep, **kwargs)
        mesh, boundaries = brep.to_viewmesh()
        self._mesh = mesh
        self._boundaries = boundaries

    @property
    def brep(self):
        return self.item

    @property
    def mesh(self):
        return self._mesh

    @property
    def boundaries(self):
        return self._boundaries

    def update(self):
        mesh, boundaries = self.brep.to_viewmesh()
        self._mesh = mesh
        self._boundaries = boundaries
        super().update()

    def _lines_data(self):
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
            color = self.linecolors.get(i, self.linecolor)
            colors.append(color)
            colors.append(color)
            elements.append([count, count + 1])
            count += 2
        return positions, colors, elements

    def _frontfaces_data(self):
        mesh = self.mesh
        vertex_xyz = {vertex: mesh.vertex_attributes(vertex, "xyz") for vertex in mesh.vertices()}
        positions = []
        colors = []
        elements = []
        i = 0
        faces = mesh.faces()
        for face in faces:
            vertices = mesh.face_vertices(face)
            color = self.facecolors.get(face, self.facecolor)
            if len(vertices) == 3:
                a, b, c = vertices
                positions.append(vertex_xyz[a])
                positions.append(vertex_xyz[b])
                positions.append(vertex_xyz[c])
                colors.append(color)
                colors.append(color)
                colors.append(color)
                elements.append([i + 0, i + 1, i + 2])
                i += 3
            elif len(vertices) == 4:
                a, b, c, d = vertices
                positions.append(vertex_xyz[a])
                positions.append(vertex_xyz[b])
                positions.append(vertex_xyz[c])
                positions.append(vertex_xyz[a])
                positions.append(vertex_xyz[c])
                positions.append(vertex_xyz[d])
                colors.append(color)
                colors.append(color)
                colors.append(color)
                colors.append(color)
                colors.append(color)
                colors.append(color)
                elements.append([i + 0, i + 1, i + 2])
                elements.append([i + 3, i + 4, i + 5])
                i += 6
            else:
                points = [vertex_xyz[vertex] for vertex in vertices]
                c = centroid_points(points)
                for a, b in pairwise(points + points[:1]):
                    positions.append(a)
                    positions.append(b)
                    positions.append(c)
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                    elements.append([i + 0, i + 1, i + 2])
                    i += 3

        return positions, colors, elements

    def _backfaces_data(self):
        mesh = self._mesh
        vertex_xyz = {vertex: mesh.vertex_attributes(vertex, "xyz") for vertex in mesh.vertices()}
        positions = []
        colors = []
        elements = []
        i = 0
        faces = mesh.faces()
        for face in faces:
            vertices = mesh.face_vertices(face)[::-1]
            color = self.facecolors.get(face, self.facecolor)
            if len(vertices) == 3:
                a, b, c = vertices
                positions.append(vertex_xyz[a])
                positions.append(vertex_xyz[b])
                positions.append(vertex_xyz[c])
                colors.append(color)
                colors.append(color)
                colors.append(color)
                elements.append([i + 0, i + 1, i + 2])
                i += 3
            elif len(vertices) == 4:
                a, b, c, d = vertices
                positions.append(vertex_xyz[a])
                positions.append(vertex_xyz[b])
                positions.append(vertex_xyz[c])
                positions.append(vertex_xyz[a])
                positions.append(vertex_xyz[c])
                positions.append(vertex_xyz[d])
                colors.append(color)
                colors.append(color)
                colors.append(color)
                colors.append(color)
                colors.append(color)
                colors.append(color)
                elements.append([i + 0, i + 1, i + 2])
                elements.append([i + 3, i + 4, i + 5])
                i += 6
            else:
                points = [vertex_xyz[vertex] for vertex in vertices]
                c = centroid_points(points)
                for a, b in pairwise(points + points[:1]):
                    positions.append(a)
                    positions.append(b)
                    positions.append(c)
                    colors.append(color)
                    colors.append(color)
                    colors.append(color)
                    elements.append([i + 0, i + 1, i + 2])
                    i += 3
        return positions, colors, elements
