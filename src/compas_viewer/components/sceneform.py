from typing import Callable
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtWidgets import QTreeWidgetItem

from compas.scene import Scene


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
    checkbox_columns : dict[int, str]
        A dictionary of column indices and their corresponding attributes.
    """

    def __init__(
        self,
        scene: Scene,
        columns: list[dict],
        column_editable: Optional[list[bool]] = None,
        show_headers: bool = True,
        callback: Optional[Callable] = None,
    ):
        super().__init__()
        self.columns = columns
        self.checkbox_columns: dict[int, str] = {}
        self.column_editable = (column_editable or [False]) + [False] * (len(columns) - len(column_editable or [False]))
        self.setColumnCount(len(columns))
        self.setHeaderLabels(col["title"] for col in self.columns)
        self.setHeaderHidden(not show_headers)

        self._scene = scene
        self.callback = callback

        self.populate_tree()

        self.itemClicked.connect(self.on_item_clicked)
        self.itemSelectionChanged.connect(self.on_item_selection_changed)

    @property
    def viewer(self):
        from compas_viewer import Viewer

        return Viewer()

    def populate_tree(self):
        self.clear()
        for node in self._scene.traverse("breadthfirst"):
            if node.is_root:
                continue

            strings = []
            for i, column in enumerate(self.columns):
                itemtype = column.get("type", None)
                action = column.get("action", None)
                kwargs = column.get("kwargs") or {}

                if action:
                    output = action(node, **kwargs)

                if itemtype == "checkbox":
                    if hasattr(node, kwargs["attr"]):
                        self.checkbox_columns[i] = kwargs["attr"]
                        output = ""
                    else:
                        raise TypeError(f"Attribute '{kwargs['attr']}' not found in node '{node}'")
                strings.append(output)

            if node.parent.is_root:
                widget = QTreeWidgetItem(self, strings)
            else:
                widget = QTreeWidgetItem(node.parent.attributes["widget"], strings)
            widget.node = node
            widget.setSelected(node.is_selected)
            widget.setFlags(widget.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)

            for col, attr in self.checkbox_columns.items():
                widget.setCheckState(col, Qt.Checked if getattr(node, attr) else Qt.Unchecked)

            node.attributes["widget"] = widget

        self.adjust_column_widths()

    def update(self):
        self.populate_tree()

    def on_item_clicked(self, item, column):
        if column in self.checkbox_columns:
            attr = self.checkbox_columns[column]
            setattr(item.node, attr, item.checkState(column) == Qt.Checked)

        if self.selectedItems():
            selected_nodes = {item.node for item in self.selectedItems()}
            for node in self._scene.objects:
                node.is_selected = node in selected_nodes
                if self.callback and node.is_selected:
                    self.callback(node)

        self.viewer.renderer.update()

    def on_item_selection_changed(self):
        for item in self.selectedItems():
            if self.callback:
                self.callback(item.node)

    def adjust_column_widths(self):
        for i in range(self.columnCount()):
            if i in self.checkbox_columns:
                self.setColumnWidth(i, 50)
