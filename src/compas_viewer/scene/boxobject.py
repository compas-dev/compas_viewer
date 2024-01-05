from compas.datastructures import Mesh
from compas.geometry import Box

from .meshobject import MeshObject


class BoxObject(MeshObject):
    """Viewer scene object for displaying COMPAS :class:`compas.geometry.Box` geometry."""

    def __init__(self, box: Box, **kwargs):
        super(BoxObject, self).__init__(mesh=Mesh.from_shape(box), **kwargs)
