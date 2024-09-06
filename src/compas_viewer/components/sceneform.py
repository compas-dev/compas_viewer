from typing import Callable
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtWidgets import QTreeWidgetItem

from compas_viewer.components.treeform import Treeform


class Sceneform(QTreeWidget):
    """
    Class for displaying the SceneTree.

    Parameters
    ----------
    scene : :class:`compas.scene.Scene`
        The scene to be displayed.
    columns : list[dict]
        A dictionary of column names and their corresponding attributes.
        Example: {"Name": lambda o: o.name, "Object": lambda o: o}
    column_editable : list[bool], optional
        A list of booleans indicating whether the corresponding column is editable. Defaults to [False].
    show_headers : bool, optional
        Show the header of the tree. Defaults to True.
    callback : Callable, optional
        Callback function to execute when an item is clicked or selected.

    Attributes
    ----------
    scene : :class:`compas.scene.Scene`
        The scene to be displayed.
    columns : list[dict]
        A dictionary of column names and their corresponding function.
    checkbox_columns : dict[int, dict[str, Callable]]
        A dictionary of column indices and their corresponding attributes.
    """

    def __init__(
        self,
        columns: list[dict],
        show_selected_tree: Optional[bool] = True,
        column_editable: Optional[list[bool]] = None,
        show_headers: Optional[bool] = True,
        callback: Optional[Callable] = None,
    ):
        super().__init__()
        self.columns = columns
        self.show_selected_tree = show_selected_tree
        self.checkbox_columns: dict[int, str] = {}
        self.column_editable = (column_editable or [False]) + [False] * (len(columns) - len(column_editable or [False]))
        self.setColumnCount(len(columns))
        self.setHeaderLabels(col["title"] for col in self.columns)
        self.setHeaderHidden(not show_headers)
        self.setSelectionMode(QTreeWidget.SingleSelection)
        self._sceneobjects = []

        self.callback = callback

        self.itemClicked.connect(self.on_item_clicked)
        self.itemSelectionChanged.connect(self.on_item_selection_changed)

    @property
    def viewer(self):
        from compas_viewer import Viewer

        return Viewer()

    @property
    def scene(self):
        return self.viewer.scene

    def update(self):
        if list(self.scene.objects) == self._sceneobjects:
            for node in self.scene.traverse("breadthfirst"):
                widget = node.attributes.get("widget")
                if widget:
                    widget.setSelected(node.is_selected)
                    if node.is_selected:
                        self.expand(node.parent)
                        self.scrollToItem(widget)
                        if self.show_selected_tree:
                            self.update_selected(node)

        else:
            self._sceneobjects = list(self.scene.objects)

            self.clear()
            self.checkbox_columns = {}

            for node in self.scene.traverse("breadthfirst"):
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

                parent_widget = self if node.parent.is_root else node.parent.attributes["widget"]
                widget = QTreeWidgetItem(parent_widget, strings)
                widget.node = node
                widget.setSelected(node.is_selected)
                if node.is_selected:
                    self.expand(node.parent)
                    if self.show_selected_tree:
                        self.update_selected(node)

                widget.setFlags(widget.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                for col, col_data in self.checkbox_columns.items():
                    widget.setCheckState(col, Qt.Checked if col_data["checked"](node) else Qt.Unchecked)

                node.attributes["widget"] = widget

            self.adjust_column_widths()

    def update_selected(self, node):
        if not hasattr(self, "treeform"):
            self.treeform = Treeform()
            self.viewer.ui.sidebar.widget.addWidget(self.treeform)

        self.treeform.update_from_dict({"objtype": node.__class__, "item": node.item, "settings": node.settings})

    def expand(self, node):
        if node.attributes.get("widget"):
            node.attributes["widget"].setExpanded(True)
            if node.parent and not node.parent.is_root:
                self.expand(node.parent)

    def on_item_clicked(self, item, column):
        if column in self.checkbox_columns:
            check = self.checkbox_columns[column]["action"]
            check(item.node, item.checkState(column) == Qt.Checked)

        if self.selectedItems():
            selected_nodes = {item.node for item in self.selectedItems()}
            for node in self.scene.objects:
                node.is_selected = node in selected_nodes
                if self.callback and node.is_selected:
                    self.callback(self, node)

            self.viewer.ui.sidebar.update()

        self.viewer.renderer.update()

    def on_item_selection_changed(self):
        for item in self.selectedItems():
            if self.callback:
                self.callback(self, item.node)

    def adjust_column_widths(self):
        for i in range(self.columnCount()):
            if i in self.checkbox_columns:
                self.setColumnWidth(i, 50)
