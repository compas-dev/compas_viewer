from collections.abc import Callable
from typing import Any
from typing import TypedDict
from typing import cast

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtWidgets import QTreeWidgetItem

from .component import Component


class SceneColumn(TypedDict, total=False):
    """Configuration for a scene-tree column."""

    title: str
    type: str
    action: Callable[[Any, bool], None]
    checked: Callable[[Any], bool]
    text: Callable[[Any], object]


class CheckboxColumn(TypedDict):
    """Callbacks used by a checkbox scene-tree column."""

    action: Callable[[Any, bool], None]
    checked: Callable[[Any], bool]


class Sceneform(Component):
    """Display and edit the viewer scene tree.

    Parameters
    ----------
    columns
        A dictionary of column names and their corresponding attributes.
        Example: {"Name": lambda o: o.name, "Object": lambda o: o}
    column_editable
        A list of booleans indicating whether the corresponding column is editable. Defaults to [False].
    show_headers
        Show the header of the tree. Defaults to True.
    action
        action function to execute when an item is clicked or selected.

    """

    def __init__(
        self,
        columns: list[SceneColumn],
        column_editable: list[bool] | None = None,
        show_headers: bool = True,
        action: Callable[[Component, Any], None] | None = None,
    ) -> None:
        super().__init__()

        self.widget = QTreeWidget()
        self.columns = columns
        self.checkbox_columns: dict[int, CheckboxColumn] = {}
        self.column_editable = (column_editable or [False]) + [False] * (len(columns) - len(column_editable or [False]))
        self.widget.setColumnCount(len(columns))
        self.widget.setHeaderLabels(cast(str, col.get("title")) for col in self.columns)
        self.widget.setHeaderHidden(not show_headers)
        self.widget.setSelectionMode(QTreeWidget.ExtendedSelection)
        self._sceneobjects: list[Any] = []
        self._refreshing = False

        self.action = action

        self.widget.itemClicked.connect(self.on_item_clicked)
        self.widget.itemSelectionChanged.connect(self.on_item_selection_changed)

    def update(self, refresh: bool = False) -> None:
        """Synchronize the tree with the scene.

        Parameters
        ----------
        refresh
            Force a full tree rebuild even when scene objects are unchanged.

        """
        self._refreshing = True
        if list(self.scene.objects) == self._sceneobjects and not refresh:
            for scene_node in self.scene.root.traverse(strategy="breadthfirst"):
                node = cast(Any, scene_node)
                widget = cast(QTreeWidgetItem | None, node.attributes.get("widget"))
                if widget:
                    widget.setSelected(node.is_selected)
                    if node.is_selected:
                        self.expand(node.parent)
                        self.widget.scrollToItem(widget)

        else:
            self._sceneobjects = list(self.scene.objects)

            self.widget.clear()
            self.checkbox_columns = {}

            for scene_node in self.scene.root.traverse(strategy="breadthfirst"):
                node = cast(Any, scene_node)
                if node.is_root:
                    continue

                strings = []

                for i, column in enumerate(self.columns):
                    type = column.get("type", None)
                    if type == "checkbox":
                        action = column.get("action")
                        checked = column.get("checked")
                        if not action or not checked:
                            raise ValueError("Both action and checked must be provided for checkbox")
                        self.checkbox_columns[i] = {"action": action, "checked": checked}
                        strings.append("")
                    elif type == "label":
                        text = column.get("text")
                        if not text:
                            raise ValueError("Text must be provided for label")
                        strings.append(text(node))

                parent_widget = self.widget if node.parent is None or node.parent.is_root else node.parent.attributes["widget"]
                widget = QTreeWidgetItem(parent_widget, strings)
                widget.node = node
                widget.setSelected(node.is_selected)
                if node.is_selected:
                    self.expand(node.parent)

                widget.setFlags(widget.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                for col, col_data in self.checkbox_columns.items():
                    widget.setCheckState(col, Qt.Checked if col_data["checked"](node) else Qt.Unchecked)

                node.attributes["widget"] = widget

            self.adjust_column_widths()
            self.widget.expandToDepth(0)
        self._refreshing = False

    def expand(self, node: Any) -> None:
        """Expand the widget hierarchy containing a scene node.

        Parameters
        ----------
        node
            Scene-tree node whose ancestors should be expanded.

        """
        if node.attributes.get("widget"):
            node.attributes["widget"].setExpanded(True)
            if node.parent and not node.parent.is_root:
                self.expand(node.parent)

    def on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Apply checkbox and selection changes from a clicked item.

        Parameters
        ----------
        item
            Clicked tree item.
        column
            Index of the clicked column.

        """
        if column in self.checkbox_columns:
            check = self.checkbox_columns[column]["action"]
            check(item.node, item.checkState(column) == Qt.Checked)

        self._sync_selection_from_widget()

    def on_item_selection_changed(self) -> None:
        """Synchronize tree selection with viewer scene objects."""
        if not self._refreshing:
            self._sync_selection_from_widget()

    def _sync_selection_from_widget(self) -> None:
        """Apply the widget selection to scene objects and refresh the viewer."""
        selected_nodes = {item.node for item in self.widget.selectedItems()}
        for node in cast(list[Any], self.scene.objects):
            node.is_selected = node in selected_nodes
            if self.action and node.is_selected:
                self.action(self, node)
        self.viewer.ui.sidebar.object_setting.update()
        self.viewer.renderer.update()

    def adjust_column_widths(self) -> None:
        """Use a compact width for checkbox columns."""
        for i in range(self.widget.columnCount()):
            if i in self.checkbox_columns:
                self.widget.setColumnWidth(i, 50)


class SceneTree(Sceneform):
    """Hierarchy-aware scene-object tree used by the default sidebar."""
