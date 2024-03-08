from typing import Union

from compas.data import Data
from compas.datastructures import Mesh
from compas.geometry import Geometry
from compas.scene import GeometryObject
from numpy import array

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject


class Collection(Data):
    """Viewer scene object for displaying a collection of COMPAS geometries."""

    def __init__(self, items: list[Union[Geometry, Mesh]], **kwargs):
        super().__init__(**kwargs)
        self.items = items

    @property
    def __data__(self):
        return self.items


class CollectionObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying a collection of COMPAS geometries."""

    def __init__(self, items: list[Union[Geometry, Mesh]], **kwargs):
        self.collection = Collection(items)
        super().__init__(geometry=self.collection, **kwargs)
        self.objects = [ViewerSceneObject(item=item, **kwargs) for item in self.collection.items]

    def _read_points_data(self) -> ShaderDataType:
        positions = []
        colors = []
        elements = []
        count = 0
        for obj in self.objects:
            p, c, e = obj._read_points_data() or ([], [], [])
            positions += p
            colors += c
            elements += (array(e) + count).tolist()
            count += len(p)
        return positions, colors, elements

    def _read_lines_data(self) -> ShaderDataType:
        positions = []
        colors = []
        elements = []
        count = 0
        for obj in self.objects:
            p, c, e = obj._read_lines_data() or ([], [], [])
            positions += p
            colors += c
            elements += (array(e) + count).tolist()
            count += len(p)
        return positions, colors, elements

    def _read_frontfaces_data(self) -> ShaderDataType:
        positions = []
        colors = []
        elements = []
        count = 0
        for obj in self.objects:
            p, c, e = obj._read_frontfaces_data() or ([], [], [])
            positions += p
            colors += c
            elements += (array(e) + count).tolist()
            count += len(p)
        return positions, colors, elements

    def _read_backfaces_data(self) -> ShaderDataType:
        positions = []
        colors = []
        elements = []
        count = 0
        for obj in self.objects:
            p, c, e = obj._read_backfaces_data() or ([], [], [])
            positions += p
            colors += c
            elements += (array(e) + count).tolist()
            count += len(p)
        return positions, colors, elements
