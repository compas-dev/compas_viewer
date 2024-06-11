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
