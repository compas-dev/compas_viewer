from compas.datastructures import Network
from compas.scene import NetworkObject as BaseNetworkObject

from .sceneobject import DataType
from .sceneobject import ViewerSceneObject


class NetworkObject(ViewerSceneObject, BaseNetworkObject):
    """Viewer scene object for displaying COMPAS Network data.


    Parameters
    ----------
    network : :class:`compas.datastructures.Network`
        The network data structure.
    **kwargs : dict, optional
        Additional options for the :class:`compas_viewer.scene.ViewerSceneObject`.

    See Also
    --------
    :class:`compas.datastructures.Network`

    """

    def __init__(self, network: Network, **kwargs):
        super(NetworkObject, self).__init__(network=network, **kwargs)
        self.network: Network

    def _read_points_data(self) -> DataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for node in self.network.nodes():
            positions.append(self.network.node_attribute(node, "xyz"))
            colors.append(self.pointscolor.get(node, self.pointscolor["_default"]))  # type: ignore
            elements.append([i])
            i += 1
        return positions, colors, elements

    def _read_lines_data(self) -> DataType:
        positions = []
        colors = []
        elements = []
        i = 0

        for u, v in self.network.edges():
            color = self.linescolor.get((u, v), self.linescolor["_default"])  # type: ignore
            positions.append(self.network.node_attribute(u, "xyz"))
            positions.append(self.network.node_attribute(v, "xyz"))
            colors.append(color)
            colors.append(color)
            elements.append([i + 0, i + 1])
            i += 2
        return positions, colors, elements
