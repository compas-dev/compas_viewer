# from compas.datastructures import Mesh
from compas.geometry import Capsule

# from compas.geometry import Line
# from compas.geometry import Point
from .shapeobject import ShapeObject


class CapsuleObject(ShapeObject):
    """Viewer scene object for displaying COMPAS Capsule geometry.

    See Also
    --------
    :class:`compas.geometry.Capsule`
    """

    def __init__(self, capsule: Capsule, **kwargs):
        super().__init__(geometry=capsule, **kwargs)
        self.geometry: Capsule

    # @property
    # def points(self) -> list[Point]:
    #     return self.polyhedron.vertices

    # @property
    # def lines(self) -> list[Line]:
    #     return self.polyhedron.lines

    # @property
    # def viewmesh(self):
    #     return Mesh.from_shape(self.geometry, u=self.u, v=self.v, triangulated=True)
