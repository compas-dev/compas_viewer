from typing import Callable
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtWidgets import QTreeWidgetItem

from compas.scene import Scene


class Sceneform(QTreeWidget):
    """
    Class for displaying the SceneTree.

    Parameters
    ----------
    scene : :class:`compas.scene.Scene`
        The tree to be displayed. An typical example is the scene
        object tree: :attr:`compas_viewer.viewer.Viewer._tree`.
    columns : dict[str, callable]
        A dictionary of column names and their corresponding attributes.
        Example: ``{"Name": (lambda o: o.name), "Object": (lambda o: o)}``
    column_editable : list, optional
        A list of booleans indicating whether the corresponding column is editable.
        Defaults to ``[False]``.
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
        scene: Scene,
        columns: dict[str, Callable],
        column_editable: list[bool] = [False],
        show_headers: bool = True,
        stretch: int = 2,
        backgrounds: Optional[dict[str, Callable]] = None,
        callback: Optional[Callable] = None,
    ):
        super().__init__()
        self.columns = columns
        self.column_editable = column_editable + [False] * (len(columns) - len(column_editable))
        self.setColumnCount(len(columns))
        self.setHeaderLabels(list(self.columns.keys()))
        self.setHeaderHidden(not show_headers)
        self.stretch = stretch
        self._backgrounds = backgrounds

        self.scene = scene
        self.callback = callback
        # TODO(pitsai): enable multiple selection
        # self.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.show_idx = self.find_column_index("Show")
        self.locked_idx = self.find_column_index("Locked")
        self.itemClicked.connect(self.on_item_clicked)
        self.itemSelectionChanged.connect(self.on_item_selection_changed)

    @property
    def viewer(self):
        from compas_viewer import Viewer

        return Viewer()

    @property
    def scene(self) -> Scene:
        return self._scene

    @scene.setter
    def scene(self, scene: Scene):
        self.clear()
        for node in scene.traverse("breadthfirst"):
            if node.is_root:
                continue

            strings = ["" if name in ["Show", "Locked"] else str(func(node)) for name, func in self.columns.items()]

            if node.parent.is_root:  # type: ignore
                widget = QTreeWidgetItem(self, strings)  # type: ignore
            else:
                widget = QTreeWidgetItem(
                    node.parent.attributes["widget"],
                    strings,  # type: ignore
                )
            widget.node = node
            widget.setSelected(node.is_selected)
            widget.setFlags(widget.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Allow checkbox

            if self.show_idx is not None:
                widget.setCheckState(self.show_idx, Qt.Checked if node.show else Qt.Unchecked)
            if self.locked_idx is not None:
                widget.setCheckState(self.locked_idx, Qt.Checked if node.is_locked else Qt.Unchecked)

            if self._backgrounds:
                for col, background in self._backgrounds.items():
                    widget.setBackground(list(self.columns.keys()).index(col), QColor(*background(node).rgb255))
            node.attributes["widget"] = widget

        self.adjust_column_widths()
        self._scene = scene

    def update(self):
        self.scene = self.viewer.scene

    def on_item_clicked(self, item, column):
        if column == self.show_idx:
            is_visible = item.checkState(self.show_idx) == Qt.Checked
            item.node.show = is_visible

        if column == self.locked_idx:
            is_locked = item.checkState(self.locked_idx) == Qt.Checked
            item.node.is_locked = is_locked

        if self.selectedItems():
            self._selected_items = self.selectedItems()
            selected_nodes = {item.node for item in self.selectedItems()}
            for node in self.scene.objects:
                node.is_selected = node in selected_nodes
                if self.callback and node.is_selected:
                    self.callback(node)

        self.viewer.renderer.update()

    def on_item_selection_changed(self):
        for item in self.selectedItems():
            if self.callback:
                self.callback(item.node)

    def adjust_column_widths(self, item=None, column=None):
        for i in range(self.columnCount()):
            self.resizeColumnToContents(i)

    def find_column_index(self, column_name):
        """Utility to find the index of a specific column by name."""
        return next((i for i, name in enumerate(self.columns) if name == column_name), None)
