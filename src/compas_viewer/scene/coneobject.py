# from compas.datastructures import Mesh
from compas.geometry import Cone

# from compas.geometry import Line
# from compas.geometry import Point
# from compas.scene import GeometryObject
from .shapeobject import ShapeObject


class ConeObject(ShapeObject):
    """Viewer scene object for displaying COMPAS Cone geometry.

    See Also
    --------
    :class:`compas.geometry.Cone`
    """

    def __init__(self, cone: Cone, **kwargs):
        super().__init__(geometry=cone, **kwargs)
        self.geometry: Cone
        # self.polyhedron = self.geometry.to_polyhedron(u=self.u, triangulated=False)

    # @property
    # def points(self) -> list[Point]:
    #     return self.polyhedron.vertices

    # @property
    # def lines(self) -> list[Line]:
    #     return self.polyhedron.lines

    # @property
    # def viewmesh(self):
    #     return Mesh.from_shape(self.geometry, u=self.u, triangulated=True)
