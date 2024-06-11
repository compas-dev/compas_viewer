from compas.geometry import Capsule

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
