from typing import TYPE_CHECKING
from typing import Optional

from compas.datastructures import Tree

if TYPE_CHECKING:
    from compas_viewer import Viewer


class CollectionObject:
    """
    Viewer scene object for displaying a group of COMPAS geometries.

    Parameters
    ----------
    viewer : :class:`compas_viewer.Viewer`
        The viewer instance.
    tree : :class:`compas.datastructures.Tree`, optional
        A tree structure for describing the hierarchy of the collection, with the data stored in the geometries.
    **kwargs : dict, optional
        Additional visualization options for specific objects.

    See Also
    --------
    :class:`compas_viewer.scene.sceneobject.SceneObject`
    """

    def __init__(
        self,
        viewer: "Viewer",
        tree: Optional[Tree] = None,
        **kwargs,
    ):
        pass

    def init_collection(self):
        self.items = [self.viewer.add(node.attributes["mesh"],  **kwargs) for node in self.tree.nodes]  # type: ignore
