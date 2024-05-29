# from compas.datastructures import Mesh
from compas.geometry import Cylinder

# from compas.geometry import Line
# from compas.geometry import Point
from .shapeobject import ShapeObject


class CylinderObject(ShapeObject):
    """Viewer scene object for displaying COMPAS Cylinder geometry.

    See Also
    --------
    :class:`compas.geometry.Cylinder`
    """

    def __init__(self, cylinder: Cylinder, **kwargs):
        super().__init__(geometry=cylinder, **kwargs)
        self.geometry: Cylinder
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
