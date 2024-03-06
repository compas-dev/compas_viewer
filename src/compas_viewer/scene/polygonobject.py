from compas.datastructures import Mesh
from compas.geometry import Polygon

from .meshobject import MeshObject


class PolygonObject(MeshObject):
    """Viewer scene object for displaying COMPAS Polygon geometry.

    See Also
    --------
    :class:`compas.geometry.Polygon`
    """

    def __init__(self, polygon: Polygon, **kwargs):
        super().__init__(mesh=Mesh.from_shape(polygon), **kwargs)
