# from compas.datastructures import Mesh
# from compas.geometry import Line
# from compas.geometry import Point
from compas.geometry import Torus

from .shapeobject import ShapeObject


class TorusObject(ShapeObject):
    """Viewer scene object for displaying COMPAS Torus geometry.

    See Also
    --------
    :class:`compas.geometry.Torus`
    """

    def __init__(self, torus: Torus, **kwargs):
        super().__init__(geometry=torus, **kwargs)
        self.geometry: Torus
        # self.polyhedron = self.geometry.to_polyhedron(u=self.u, v=self.v, triangulated=False)

    # @property
    # def points(self) -> list[Point]:
    #     return self.polyhedron.vertices

    # @property
    # def lines(self) -> list[Line]:
    #     return self.polyhedron.lines

    # @property
    # def viewmesh(self):
    #     return Mesh.from_shape(self.geometry, u=self.u, v=self.v, triangulated=True)
