from typing import Callable
from typing import Optional

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtWidgets import QTreeWidgetItem

from compas.datastructures import Tree
from compas.datastructures import TreeNode


class Treeform(QTreeWidget):
    """
    Class for displaying tree-like data.
    Treeform is an abstract class that could be placed in either the viewport or the sidedock.

    Parameters
    ----------
    tree : :class:`compas.datastructures.Tree`
        The tree to be displayed. An typical example is the scene
        object tree: :attr:`compas_viewer.viewer.Viewer._tree`.
    columns : dict[str, callable]
        A dictionary of column names and their corresponding attributes.
        Example: ``{"Name": (lambda o: o.name), "Object": (lambda o: o)}``
    show_headers : bool, optional
        Show the header of the tree.
        Defaults to ``True``.
    stretch : int, optional
        Stretch factor of the tree in the grid layout.
        Defaults to ``2``.
    backgrounds : dict[str, callable], optional
        A dictionary of column names and their corresponding color.
        Example: ``{"Object-Color": (lambda o: o.surfacecolor)}``

    Attributes
    ----------
    tree : :class:`compas.datastructures.Tree`
        The tree to be displayed.

    See Also
    --------
    :class:`compas.datastructures.Tree`
    :class:`compas.datastructures.tree.TreeNode`
    :class:`compas_viewer.layout.SidedockLayout`

    References
    ----------
    :PySide6:`PySide6/QtWidgets/QTreeWidget`

    Examples
    --------
    .. code-block:: python

        from compas_viewer import Viewer

        viewer = Viewer()

        for i in range(10):
            for j in range(10):
                sp = viewer.scene.add(Sphere(0.1, Frame([i, j, 0], [1, 0, 0], [0, 1, 0])), name=f"Sphere_{i}_{j}")

        viewer.layout.sidedock.add_element(Treeform(viewer._tree, {"Name": (lambda o: o.object.name), "Object": (lambda o: o.object)}))

        viewer.show()

    """

    def __init__(
        self,
        tree: Tree = None,
        columns: dict[str, Callable] = None,
        show_headers: bool = True,
        stretch: int = 2,
        backgrounds: Optional[dict[str, Callable]] = None,
        callback: Optional[Callable] = None,
    ):
        super().__init__()
        self.columns = columns or {"Name": lambda node: node.name, "Value": lambda node: node.attributes.get("value", "")}
        self.setColumnCount(len(self.columns))
        self.setHeaderLabels(list(self.columns.keys()))
        self.setHeaderHidden(not show_headers)
        self.stretch = stretch
        self._backgrounds = backgrounds

        self.tree = tree or Tree()
        self.callback = callback
        self.itemSelectionChanged.connect(self.on_item_selection_changed)

    def update(self):
        self.clear()
        for node in self.tree.traverse("breadthfirst"):
            if node.is_root:
                continue

            strings = [str(c(node)) for _, c in self.columns.items()]

            if node.parent.is_root:  # type: ignore
                node.attributes["widget_item"] = QTreeWidgetItem(self, strings)  # type: ignore
            else:
                node.attributes["widget_item"] = QTreeWidgetItem(
                    node.parent.attributes["widget_item"],
                    strings,  # type: ignore
                )

            node.attributes["widget_item"].node = node

            if self._backgrounds:
                for col, background in self._backgrounds.items():
                    node.attributes["widget_item"].setBackground(list(self.columns.keys()).index(col), QColor(*background(node).rgb255))

    def tree_from_dict(self, data):
        tree = Tree()
        root = TreeNode("Root")
        tree.add(root)

        def add_children(key, data, parent):
            if isinstance(data, dict):
                node = TreeNode(name=key)
                for child_key, child_data in data.items():
                    add_children(child_key, child_data, node)
            elif isinstance(data, (list, tuple)):
                node = TreeNode(name=key)
                for child_index, child_data in enumerate(data):
                    add_children(child_index, child_data, node)
            else:
                node = TreeNode(name=key, value=data)

            parent.add(node)

        for key, data in data.items():
            add_children(key, data, root)

        return tree

    def update_from_dict(self, data):
        self.tree = self.tree_from_dict(data)
        self.update()

    def on_item_selection_changed(self):
        for item in self.selectedItems():
            if self.callback:
                self.callback(item.node)
