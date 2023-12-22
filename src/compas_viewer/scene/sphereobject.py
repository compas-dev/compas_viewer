from compas.scene import GeometryObject
from .sceneobject import ViewerSceneObject


class SphereObject(ViewerSceneObject, GeometryObject):
    """Scene object for drawing sphere shapes.

    Parameters
    ----------
    box : :class:`compas.geometry.Sphere`
        A COMPAS sphere.
    **kwargs : dict, optional
        Additional keyword arguments.

    """

    def __init__(self, sphere, **kwargs):
        super(SphereObject, self).__init__(geometry=sphere, **kwargs)

    def draw(self):
        """Draw the box associated with the object."""
        raise NotImplementedError
