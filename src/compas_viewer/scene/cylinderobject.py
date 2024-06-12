from compas.geometry import Cylinder

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
