from typing import Optional

from compas.colors import Color
from compas.datastructures import Mesh
from compas.datastructures import Tree
from compas.datastructures import TreeNode
from compas.geometry import centroid_points
from compas.geometry import is_coplanar
from compas.utilities import pairwise

from .collectionobject import CollectionObject
from .meshobject import MeshObject
from .sceneobject import DataType

try:
    from compas_robots import RobotModel
    from compas_robots.scene import BaseRobotModelObject

    class RobotModelObject(BaseRobotModelObject, CollectionObject):
        """Viewer scene object for displaying COMPAS Robot geometry.

        Parameters
        ----------
        model : :class:`compas_robots.RobotModel`
            Robot model.
        geometry_type : tuple[bool,bool,bool], optional
            Geometry types to display (draw_visual, draw_collision, draw_attached_meshes). Defaults to (True, False, True).
        **kwargs : dict, optional
            Additional keyword arguments.
            For more info,
            see :class:`compas_viewer.scene.MeshObject` and :class:`compas_robots.scene.BaseRobotModelObject`.

        Attributes
        ----------
        mesh : :class:`compas.datastructures.Mesh`
            The mesh data structure.

        See Also
        --------
        :class:`compas_robots.scene.BaseRobotModelObject`
        :class:`compas.datastructures.Mesh`
        """

        def __init__(
            self, item: RobotModel, viewer, geometry_type: tuple[bool, bool, bool] = (True, False, True), **kwargs
        ):
            super(RobotModelObject, self).__init__(model=item, viewer=viewer, **kwargs)
            self.viewer = viewer
            self.tree = Tree()
            root = TreeNode(name="root")
            self.tree.add(root)

            if geometry_type[0]:
                for i, mesh in enumerate(self.draw_visual()):
                    node = TreeNode()
                    node.attributes["mesh"] = mesh
                    if i == 0:
                        root.add(node)
                    else:
                        _node = TreeNode()
                        node.add(_node)
                        node = _node

            elif geometry_type[1]:
                for i, mesh in enumerate(self.draw_collision()):
                    node = TreeNode()
                    node.attributes["mesh"] = mesh

                    if i == 0:
                        root.add(node)
                    else:
                        _node = TreeNode()
                        node.add(_node)
                        node = _node

            # if geometry_type[2]:
            #     list(self.tree.nodes)[-1].add(TreeNode(data=self.draw_attached_meshes()))
            self.init_collection()

        def transform(self, native_mesh, transformation):
            pass

        def create_geometry(self, geometry, name=None, color=None):
            """Create the scene object representing the robot geometry.

            Parameters
            ----------
            geometry : :class:`~compas.datastructures.Mesh`
                Instance of a mesh data structure
            name : str, optional
                The name of the mesh to draw.
            color : :class:`~compas.colors.Color`
                The color of the object.`

            Returns
            -------
            :class:`compas.datastrctures.Mesh`
            """

            return geometry

        def draw(self):
            """Draw the visual meshes of the robot model."""
            return self.draw_visual()

except ImportError:
    pass
