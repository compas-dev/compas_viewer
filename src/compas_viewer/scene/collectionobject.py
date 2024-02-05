from compas.scene import GeometryObject
from compas.data import Data
from .sceneobject import DataType
from .sceneobject import ViewerSceneObject
import numpy as np


class Collection(Data):
    def __init__(self, items: list, **kwargs):
        super(Collection, self).__init__(**kwargs)
        self.items = items

    @property
    def __data__(self):
        return self.items


class CollectionObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying a collection of COMPAS geometries."""

    def __init__(self, items: list, **kwargs):
        collection = Collection(items)
        super(CollectionObject, self).__init__(geometry=collection, **kwargs)
        self.collection = collection
        self.objects = [ViewerSceneObject(item, **kwargs) for item in self.collection.items]

    def _read_points_data(self) -> DataType:
        positions = []
        colors = []
        elements = []
        count = 0
        for obj in self.objects:
            p, c, e = obj._read_points_data() or ([], [], [])
            positions += p
            colors += c
            elements += (np.array(e) + count).tolist()
            count += len(p)
        return positions, colors, elements

    def _read_lines_data(self):
        positions = []
        colors = []
        elements = []
        count = 0
        for obj in self.objects:
            p, c, e = obj._read_lines_data() or ([], [], [])
            positions += p
            colors += c
            elements += (np.array(e) + count).tolist()
            count += len(p)
        return positions, colors, elements

    def _read_frontfaces_data(self):
        positions = []
        colors = []
        elements = []
        count = 0
        for obj in self.objects:
            p, c, e = obj._read_frontfaces_data() or ([], [], [])
            positions += p
            colors += c
            elements += (np.array(e) + count).tolist()
            count += len(p)
        return positions, colors, elements

    def _read_backfaces_data(self):
        positions = []
        colors = []
        elements = []
        count = 0
        for obj in self.objects:
            p, c, e = obj._read_backfaces_data() or ([], [], [])
            positions += p
            colors += c
            elements += (np.array(e) + count).tolist()
            count += len(p)
        return positions, colors, elements
