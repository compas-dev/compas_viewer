from compas.geometry import Cone

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
