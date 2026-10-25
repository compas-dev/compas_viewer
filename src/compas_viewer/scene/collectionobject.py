from typing import Any
from typing import cast

import numpy as np
from numpy import array

from compas.data import Data
from compas.datastructures import Mesh
from compas.geometry import Geometry
from compas.scene import GeometryObject

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject


class Collection(Data):
    def __init__(self, items: list[Geometry | Mesh] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.items = items or []

    @property
    def __data__(self) -> dict[str, list[Geometry | Mesh]]:
        return {"items": self.items}


class CollectionObject(ViewerSceneObject, GeometryObject):
    """Viewer scene object for displaying a collection of COMPAS geometries."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        kwargs.pop("item")
        self.objects = [ViewerSceneObject(item=item, **kwargs) for item in self.collection.items]

    @property
    def collection(self) -> Collection:
        return cast(Collection, self.item)

    def _read_points_data(self) -> ShaderDataType:
        positions: list[Any] = []
        colors: list[Any] = []
        elements: list[Any] = []
        count = 0
        for obj in self.objects:
            p, c, e = obj._read_points_data() or ([], [], [])
            positions.extend(p)
            if c is not None:
                colors.extend(c)
            elements += (array(e) + count).tolist()
            count += len(p)

        return positions, colors, elements

    def _read_lines_data(self) -> ShaderDataType:
        positions: list[Any] = []
        colors: list[Any] = []
        elements: list[Any] = []
        count = 0
        for obj in self.objects:
            p, c, e = obj._read_lines_data() or ([], [], [])
            positions.extend(p)
            if c is not None:
                colors.extend(c)
            elements += (array(e) + count).tolist()
            count += len(p)

        return positions, colors, elements

    def _read_frontfaces_data(self) -> ShaderDataType:
        positions: list[Any] = []
        colors: list[Any] = []
        elements: list[Any] = []
        count = 0
        for obj in self.objects:
            p, c, e = obj._read_frontfaces_data() or ([], [], [])
            positions.extend(p)
            if c is not None:
                colors.extend(c)
            elements += (np.array(e) + count).tolist()
            count += len(p)

        return positions, colors, elements

    def _read_backfaces_data(self) -> ShaderDataType:
        positions: list[Any] = []
        colors: list[Any] = []
        elements: list[Any] = []
        count = 0
        for obj in self.objects:
            p, c, e = obj._read_backfaces_data() or ([], [], [])
            positions.extend(p)
            if c is not None:
                colors.extend(c)
            elements += (np.array(e) + count).tolist()
            count += len(p)

        return positions, colors, elements
