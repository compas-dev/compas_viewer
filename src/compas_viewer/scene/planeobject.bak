from compas.geometry import Line
from compas.geometry import Frame
from compas.datastructures import Mesh
from compas.geometry import Plane

from .meshobject import MeshObject
from .lineobject import LineObject
from .compositeobject import CompositeObject


class PlaneObject(CompositeObject):
    """Object for displaying COMPAS Plane geometry."""

    def __init__(self, data, size=1, **kwargs):
        self._data = data
        self.frame = Frame.from_plane(data)

        line = Line(self.frame.to_world_coordinates([0, 0, 0]), self.frame.to_world_coordinates([0, 0, size]))
        lineObject = LineObject(line, **kwargs)

        vertices = [
            self.frame.to_world_coordinates([-size, -size, 0]),
            self.frame.to_world_coordinates([size, -size, 0]),
            self.frame.to_world_coordinates([size, size, 0]),
            self.frame.to_world_coordinates([-size, size, 0]),
        ]
        faces = [[0, 1, 2], [0, 2, 3]]
        mesh = Mesh.from_vertices_and_faces(vertices, faces)
        meshObject = MeshObject(mesh, hide_coplanaredges=True, **kwargs)

        super().__init__([meshObject, lineObject], **kwargs)

    @classmethod
    def create_default(cls) -> Plane:
        return Plane([0, 0, 0], [0, 0, 1])
