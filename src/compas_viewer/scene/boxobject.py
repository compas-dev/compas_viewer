from compas.scene import GeometryObject
from .sceneobject import ViewerSceneObject


class BoxObject(ViewerSceneObject, GeometryObject):
    """Scene object for drawing box shapes.

    Parameters
    ----------
    box : :class:`compas.geometry.Box`
        A COMPAS box.
    **kwargs : dict, optional
        Additional keyword arguments.

    """

    def __init__(self, box, **kwargs):
        super(BoxObject, self).__init__(geometry=box, **kwargs)

    def draw(self):
        """Draw the box associated with the object."""
        raise NotImplementedError
