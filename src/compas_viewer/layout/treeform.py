from compas.datastructures import Tree
from compas.datastructures import TreeNode
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
    columns : dict, optional
        A dictionary of column names and their corresponding attributes.
        Defaults to ``{"Name": ["object", "name"], "Object": ["object"]}``.
    column_editable : list, optional
        A list of booleans indicating whether the corresponding column is editable.
        Defaults to ``[False]``.
    show_headers : bool, optional
        Show the header of the tree.
        Defaults to ``True``.
    stretch : int, optional
        Stretch factor of the tree in the grid layout.
        Defaults to ``2``.

    Attributes
    ----------
    tree : :class:`compas.datastructures.Tree`
        The tree to be displayed.

    See Also
    --------
    :class:`compas.datastructures.Tree`
    :class:`compas.datastructures.TreeNode`
    :class:`compas_viewer.layout.SidedockLayout`

    References
    ----------
    :PySide6:`PySide6/QtWidgets/QTreeWidget`
    """

    def __init__(
        self,
        tree: Tree,
        columns: dict[str, list[str]] = {"Name": ["object", "name"], "Object": ["object"]},
        column_editable: list[bool] = [False],
        show_headers: bool = True,
        stretch: int = 2,
    ):
        super().__init__()
        self.columns = columns
        self.column_editable = column_editable + [False] * (len(columns) - len(column_editable))
        self.setColumnCount(len(columns))
        self.setHeaderLabels(list(self.columns.keys()))
        self.setHeaderHidden(not show_headers)
        self.stretch = stretch

        self.tree = tree
        self._tree: Tree

    @property
    def tree(self) -> Tree:
        return self._tree

    @tree.setter
    def tree(self, tree: Tree):
        for node in tree.traverse("breadthfirst"):
            strings = [self.column_attributes(node, c) for _, c in self.columns.items()]
            if node.is_root:
                continue
            elif node.parent.is_root:  # type: ignore
                node.attributes["widget_item"] = QTreeWidgetItem(self, strings)  # type: ignore
            else:
                node.attributes["widget_item"] = QTreeWidgetItem(
                    node.parent.attributes["widget_item"], strings  # type: ignore
                )
        self._tree = tree

    def column_attributes(self, node: TreeNode, list_of_strings: list[str]) -> str:
        """This function finds the attribute names and serializes it to a string by the
        given ``columns`` template format.

        Parameters
        ----------
        node : :class:`compas.datastructures.TreeNode`
            The node to be serialized.
        list_of_strings : list of str
            The list of strings that describes the attribute path.

        Returns
        -------
        str
            The serialized string.
        """
        attr = node
        for string in list_of_strings:
            if attr is None:
                break
            elif isinstance(string, dict):
                attr = attr[string]  # type: ignore
            else:
                attr = getattr(attr, string, None)
        return str(attr)
