from typing import Optional

from compas.datastructures import Tree
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtWidgets import QTreeWidgetItem


class Treeform(QTreeWidget):
    """
    Class for displaying tree-like data.
    Treeform is an abstract class that could be placed in either the viewport or the sidedock.

    Parameters
    ----------
    tree : :class:`compas.datastructures.Tree`
        The tree to be displayed. An typical example is the scene
        object tree: :attr:`compas_viewer.viewer.Viewer._tree`.
    columns : dict
        A dictionary of column names and their corresponding attributes.
        Example: `` {"Name": "object.name", "Object": "object"}``
    column_editable : list, optional
        A list of booleans indicating whether the corresponding column is editable.
        Defaults to ``[False]``.
    show_headers : bool, optional
        Show the header of the tree.
        Defaults to ``True``.
    stretch : int, optional
        Stretch factor of the tree in the grid layout.
        Defaults to ``2``.
    backgrounds : dict[object, :class:`compas.colors.Color`], optional
        A dictionary of column names and their corresponding color.
        Example: `` {"Name": "object.surfacecolor"}``

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

        viewer.layout.sidedock.add_element(Treeform(viewer._tree, {"Name":".object.name", "Object":".object"}))

        viewer.show()

    """

    def __init__(
        self,
        tree: Tree,
        columns: dict[str, str],
        column_editable: list[bool] = [False],
        show_headers: bool = True,
        stretch: int = 2,
        backgrounds: Optional[dict[str, str]] = None,
    ):
        super().__init__()
        self.columns = columns
        self.column_editable = column_editable + [False] * (len(columns) - len(column_editable))
        self.setColumnCount(len(columns))
        self.setHeaderLabels(list(self.columns.keys()))
        self.setHeaderHidden(not show_headers)
        self.stretch = stretch
        self._backgrounds = backgrounds

        self.tree = tree
        self._tree = tree

    @property
    def tree(self) -> Tree:
        return self._tree

    @tree.setter
    def tree(self, tree: Tree):
        self.clear()
        for node in tree.traverse("breadthfirst"):
            if node.is_root:
                continue

            strings = [eval(f"str(node{c})", globals(), {"node": node}) for _, c in self.columns.items()]

            if node.parent.is_root:  # type: ignore
                node.attributes["widget_item"] = QTreeWidgetItem(self, strings)  # type: ignore
            else:
                node.attributes["widget_item"] = QTreeWidgetItem(
                    node.parent.attributes["widget_item"], strings  # type: ignore
                )

            if self._backgrounds:
                for col, background in self._backgrounds.items():
                    node.attributes["widget_item"].setBackground(
                        list(self.columns.keys()).index(col),
                        eval(f"QColor(*node{background}.rgb255)", globals(), {"node": node, "background": background}),
                    )

    def update(self):
        self.tree = self._tree
