from compas.datastructures import Graph
from compas.scene import GraphObject as BaseGraphObject

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject


class GraphObject(ViewerSceneObject, BaseGraphObject):
    """Viewer scene object for displaying COMPAS Graph data."""

    graph: Graph

    def _read_points_data(self) -> ShaderDataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for node in self.graph.nodes():
            positions.append(self.graph.node_coordinates(node))
            colors.append(self.nodecolor.default)
            elements.append([i])
            i += 1
        return positions, colors, elements

    def _read_lines_data(self) -> ShaderDataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for u, v in self.graph.edges():
            color = self.edgecolor.default
            positions.append(self.graph.node_coordinates(u))
            positions.append(self.graph.node_coordinates(v))
            colors.append(color)
            colors.append(color)
            elements.append([i + 0, i + 1])
            i += 2
        return positions, colors, elements
