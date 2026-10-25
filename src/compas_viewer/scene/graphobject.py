from typing import Protocol
from typing import cast

from compas.colors import Color
from compas.scene import GraphObject as BaseGraphObject

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject


class ColorLookup(Protocol):
    def __getitem__(self, key: object) -> Color: ...


class GraphObject(ViewerSceneObject, BaseGraphObject):
    """Viewer scene object for displaying COMPAS Graph data."""

    def _read_points_data(self) -> ShaderDataType:
        positions = []
        colors = []
        elements = []
        i = 0

        nodecolors = cast(ColorLookup, self.nodecolor)
        for node in self.graph.nodes():
            positions.append(self.graph.node_coordinates(node))
            colors.append(nodecolors[node])
            elements.append([i])
            i += 1
        return positions, colors, elements

    def _read_lines_data(self) -> ShaderDataType:
        positions = []
        colors = []
        elements = []
        i = 0

        edgecolors = cast(ColorLookup, self.edgecolor)
        for u, v in self.graph.edges():
            color = edgecolors[(u, v)]
            positions.append(self.graph.node_coordinates(u))
            positions.append(self.graph.node_coordinates(v))
            colors.append(color)
            colors.append(color)
            elements.append([i + 0, i + 1])
            i += 2
        return positions, colors, elements
