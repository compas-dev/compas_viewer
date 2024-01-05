from compas.datastructures import Mesh
from compas.geometry import Polygon

from .meshobject import MeshObject


class PolygonObject(MeshObject):
    """Viewer scene object for displaying COMPAS :class:`compas.geometry.Polygon` geometry."""

    def __init__(self, polygon: Polygon, **kwargs):
        super(PolygonObject, self).__init__(mesh=Mesh.from_shape(polygon), **kwargs)
