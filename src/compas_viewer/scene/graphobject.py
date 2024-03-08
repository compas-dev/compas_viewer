from typing import Optional

from compas.datastructures import Graph
from compas.geometry import Line
from compas.geometry import Point
from compas.scene import GraphObject as BaseGraphObject

from .geometryobject import GeometryObject as ViewerGeometryObject


class GraphObject(ViewerGeometryObject, BaseGraphObject):
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
        super().__init__(graph=graph, **kwargs)
        self.graph: Graph

    @property
    def points(self) -> Optional[list[Point]]:
        """The points to be shown in the viewer."""
        return [Point(*self.graph.node_coordinates(node)) for node in self.graph.nodes()]

    @property
    def lines(self) -> Optional[list[Line]]:
        """The lines to be shown in the viewer."""
        return [Line(self.graph.node_coordinates(u), self.graph.node_coordinates(v)) for u, v in self.graph.edges()]

    @property
    def viewmesh(self):
        """The mesh volume to be shown in the viewer."""
        return None
