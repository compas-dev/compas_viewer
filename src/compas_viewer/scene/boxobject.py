from compas.datastructures import Mesh

from .meshobject import MeshObject


class BoxObject(MeshObject):
    """Viewer scene object for displaying COMPAS :class:`compas.geometry.Box` geometry."""

    def __init__(self, data, **kwargs):
        super().__init__(Mesh.from_shape(data), **kwargs)
        self._data = data

    def update(self):
        self._mesh = Mesh.from_shape(self._data)
        super().update()
