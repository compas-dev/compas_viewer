from typing import Union

import numpy as np
from numpy import array

from compas.data import Data
from compas.datastructures import Mesh
from compas.geometry import Geometry
from compas.scene import GeometryObject

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject


class Collection(Data):
    def __init__(self, items: list[Union[Geometry, Mesh]] = None, **kwargs):
        super().__init__(**kwargs)
        self.items = items

    @property
    def __data__(self):
        return {"items": self.items}


class CollectionObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying a collection of COMPAS geometries."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        kwargs.pop("item")
        self.objects = [ViewerSceneObject(item=item, **kwargs) for item in self.collection.items]

    @property
    def collection(self) -> Collection:
        return self.item

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
            elements += (np.array(e) + count).tolist()
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
            elements += (np.array(e) + count).tolist()
            count += len(p)

        return positions, colors, elements
