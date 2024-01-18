from typing import TYPE_CHECKING

from compas.datastructures import Tree
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget

from .elements import Treeform

if TYPE_CHECKING:
    from .layout import Layout


class SidedockLayout:
    """
    The SidedockLayout class manages all
    the layout and other UI-related information of the side dock itself.

    Parameters
    ----------
    layout : :class:`compas_viewer.layout.Layout`
        The parent layout.

    Attributes
    ----------
    layout : :class:`compas_viewer.layout.Layout`
        The parent layout.
    viewer : :class:`compas_viewer.viewer.Viewer`
        The parent viewer.
    config : :class:`compas_viewer.configurations.WindowConfig`
        The window configuration.

    See Also
    --------
    :class:`compas_viewer.configurations.layout_config.SidedockConfig`

    References
    ----------
    :PySide6:`PySide6/QtWidgets/QDockWidget`
    """

    def __init__(self, layout: "Layout"):
        self.layout = layout
        self.viewer = self.layout.viewer
        self.config = layout.config.window
        self.config = layout.config.toolbar
        self.sidedock = QDockWidget()
        self.sidedock.setMinimumWidth(200)

    def init(self):
        from compas.datastructures import Tree
        from compas.datastructures import TreeNode
        from compas.geometry import Point

        tree = Tree()
        root = TreeNode(name="root", data= Point(0,0,0))
        branch = TreeNode(name="branch")
        branch2 = TreeNode(name="branch2")
        leaf1 = TreeNode(name="leaf1")
        leaf2 = TreeNode(name="leaf2")
        leaf3 = TreeNode(name="leaf3")
        leaf4 = TreeNode(name="leaf4")
        tree.add(root)
        root.add(branch)
        branch.add(leaf1)
        branch.add(leaf2)
        branch2.add(leaf3)
        root.add(branch2)
        branch2.add(leaf4)

        # self.sidedock.setWidget(Treeform(self.viewer.tree))
        self.sidedock.setWidget(Treeform(tree))
        self.viewer.window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.sidedock)
