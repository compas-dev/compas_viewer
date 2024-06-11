from compas.geometry import Box

from .shapeobject import ShapeObject


class BoxObject(ShapeObject):
    """Viewer scene object for displaying COMPAS Box geometry.

    See Also
    --------
    :class:`compas.geometry.Box`
    """

    def __init__(self, box: Box, **kwargs):
        super().__init__(geometry=box, **kwargs)
        self.geometry: Box
