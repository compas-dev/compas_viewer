from compas.datastructures import Graph
from compas.scene import GraphObject as BaseGraphObject

from .sceneobject import DataType
from .sceneobject import ViewerSceneObject


class GraphObject(ViewerSceneObject, BaseGraphObject):
    """Viewer scene object for displaying COMPAS Graph data.


    Parameters
    ----------
    graph : :class:`compas.datastructures.Graph`
        The graph data structure.
    **kwargs : dict, optional
        Additional options for the :class:`compas_viewer.scene.ViewerSceneObject`.

    See Also
    --------
    :class:`compas.datastructures.Graph`

    """

    def __init__(self, graph: Graph, **kwargs):
        super(GraphObject, self).__init__(graph=graph, **kwargs)
        self.graph: Graph

    def _read_points_data(self) -> DataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for node in self.graph.nodes():
            positions.append(self.graph.node_coordinates(node))
            colors.append(self.pointscolor.get(node, self.pointscolor["_default"]))  # type: ignore
            elements.append([i])
            i += 1
        return positions, colors, elements

    def _read_lines_data(self) -> DataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for u, v in self.graph.edges():
            color = self.linescolor.get((u, v), self.linescolor["_default"])  # type: ignore
            positions.append(self.graph.node_coordinates(u))
            positions.append(self.graph.node_coordinates(v))
            colors.append(color)
            colors.append(color)
            elements.append([i + 0, i + 1])
            i += 2
        return positions, colors, elements
