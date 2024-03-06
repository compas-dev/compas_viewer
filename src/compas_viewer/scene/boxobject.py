from compas.datastructures import Mesh
from compas.geometry import Box

from .meshobject import MeshObject


class BoxObject(MeshObject):
    """Viewer scene object for displaying COMPAS Box geometry.

    See Also
    --------
    :class:`compas.geometry.Box`
    """

    def __init__(self, box: Box, **kwargs):
        super().__init__(mesh=Mesh.from_shape(box), **kwargs)
