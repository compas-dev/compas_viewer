from typing import Protocol
from typing import cast

from compas.colors import Color

from .sceneobject import ShaderDataType
from .sceneobject import ViewerSceneObject


class ColorLookup(Protocol):
    def __getitem__(self, key: object) -> Color: ...


class GraphObject(ViewerSceneObject):
    """Viewer scene object for displaying COMPAS Graph data."""

    @property
    def show_points(self) -> bool:
        """Whether graph nodes are visible in the point channel."""
        return bool(self.show_nodes)

    @show_points.setter
    def show_points(self, show: bool) -> None:
        self.show_nodes = show

    @property
    def show_lines(self) -> bool:
        """Whether graph edges are visible in the line channel."""
        return bool(self.show_edges)

    @show_lines.setter
    def show_lines(self, show: bool) -> None:
        self.show_edges = show

    @property
    def show_faces(self) -> bool:
        """Graph render helpers never contribute a face channel."""
        return False

    @show_faces.setter
    def show_faces(self, show: bool) -> None:
        if show:
            raise ValueError("Graphs do not provide a face render channel.")

    @property
    def pointsize(self) -> float:
        """Node size used by the generic Viewer buffer contract."""
        return self.nodesize

    @pointsize.setter
    def pointsize(self, size: float) -> None:
        self.nodesize = size

    @property
    def linewidth(self) -> float:
        """Edge width used by the generic Viewer buffer contract."""
        return self.edgewidth

    @linewidth.setter
    def linewidth(self, width: float) -> None:
        self.edgewidth = width

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
