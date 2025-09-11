from typing import Callable
from typing import Optional

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtWidgets import QTreeWidgetItem

from compas.datastructures import Tree
from compas.datastructures import TreeNode

from .component import Component


class Treeform(Component):
    """
    A component for displaying hierarchical tree-like data in a tree widget.

    This component provides a flexible way to visualize tree structures with
    customizable columns and background colors. It supports selection callbacks
    and can be used in various UI layouts.

    Parameters
    ----------
    tree : Tree, optional
        The tree data structure to display. Defaults to an empty tree.
    columns : dict[str, Callable], optional
        Dictionary mapping column names to functions that extract values from tree nodes.
        Defaults to {"Name": lambda node: node.name, "Value": lambda node: node.attributes.get("value", "")}.
    show_headers : bool, optional
        Whether to show column headers. Defaults to True.
    stretch : int, optional
        Stretch factor for the tree widget in grid layouts. Defaults to 2.
    backgrounds : dict[str, Callable], optional
        Dictionary mapping column names to functions that return background colors.
    action : Callable, optional
        Function to call when tree items are selected. Receives the selected node as argument.

    Attributes
    ----------
    widget : QTreeWidget
        The Qt tree widget for displaying the data.
    tree : Tree
        The tree data structure being displayed.
    columns : dict[str, Callable]
        Column definitions for the tree display.
    stretch : int
        Stretch factor for layout purposes.
    action : Callable or None
        Selection action function.

    Examples
    --------
    >>> # Create a simple tree form
    >>> treeform = Treeform()
    >>> treeform.update()

    >>> # Create with custom columns
    >>> columns = {"Name": lambda node: node.name, "Type": lambda node: type(node).__name__}
    >>> treeform = Treeform(columns=columns)

    >>> # Create with selection action
    >>> def on_select(node):
    ...     print(f"Selected: {node.name}")
    >>> treeform = Treeform(action=on_select)
    """

    def __init__(
        self,
        tree: Tree = None,
        columns: dict[str, Callable] = None,
        show_headers: bool = True,
        stretch: int = 2,
        backgrounds: Optional[dict[str, Callable]] = None,
        action: Optional[Callable] = None,
    ):
        super().__init__()
        self.widget = QTreeWidget()

        self.columns = columns or {"Name": lambda node: node.name, "Value": lambda node: node.attributes.get("value", "")}
        self.widget.setColumnCount(len(self.columns))
        self.widget.setHeaderLabels(list(self.columns.keys()))
        self.widget.setHeaderHidden(not show_headers)
        self.stretch = stretch
        self._backgrounds = backgrounds

        self.tree = tree or Tree()
        self.action = action
        self.widget.itemSelectionChanged.connect(self.on_item_selection_changed)

    def update(self):
        """Update the tree widget display with the current tree data.

        This method clears the existing tree widget items and rebuilds the display
        based on the current tree structure, applying column mappings and background
        colors as configured.
        """
        self.widget.clear()
        for node in self.tree.traverse("breadthfirst"):
            if node.is_root:
                continue

            strings = [str(c(node)) for _, c in self.columns.items()]

            if node.parent.is_root:  # type: ignore
                node.attributes["widget_item"] = QTreeWidgetItem(self.widget, strings)  # type: ignore
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
        """Create a tree structure from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary containing the hierarchical data to convert to a tree.

        Returns
        -------
        Tree
            A new Tree object representing the dictionary structure.
        """
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
        """Update the tree display from a dictionary structure.

        This is a convenience method that converts dictionary data to a tree
        and updates the display in one step.

        Parameters
        ----------
        data : dict
            Dictionary containing the hierarchical data to display.
        """
        self.tree = self.tree_from_dict(data)
        self.update()

    def on_item_selection_changed(self):
        """Handle tree item selection changes.

        This method is called when the selection in the tree widget changes.
        It calls the action function (if provided) with the selected node as argument.
        """
        for item in self.widget.selectedItems():
            if self.action:
                self.action(item.node)
