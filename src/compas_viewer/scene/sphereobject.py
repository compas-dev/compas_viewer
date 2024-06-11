from compas.geometry import Sphere

from .shapeobject import ShapeObject


class SphereObject(ShapeObject):
    """Viewer scene object for displaying COMPAS Sphere geometry.

    See Also
    --------
    :class:`compas.geometry.Sphere`
    """

    def __init__(self, sphere: Sphere, **kwargs):
        super().__init__(geometry=sphere, **kwargs)
        self.geometry: Sphere
