from typing import Callable
from typing import Optional

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
        self.itemClicked.connect(self.on_item_clickded)
        self.itemSelectionChanged.connect(self.on_item_selection_changed)

    @property
    def scene(self) -> Scene:
        return self._scene

    @scene.setter
    def scene(self, scene: Scene):
        self.clear()
        for node in scene.traverse("breadthfirst"):
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
            node.attributes["widget_item"].setSelected(node.is_selected)

            if self._backgrounds:
                for col, background in self._backgrounds.items():
                    node.attributes["widget_item"].setBackground(list(self.columns.keys()).index(col), QColor(*background(node).rgb255))

        self._scene = scene

    def update(self):
        from compas_viewer import Viewer

        self.scene = Viewer().scene

    def on_item_clickded(self):
        selected_nodes = [item.node for item in self.selectedItems()]
        for node in self.scene.objects:
            node.is_selected = node in selected_nodes
            if self.callback and node.is_selected:
                self.callback(node)

        from compas_viewer import Viewer

        Viewer().renderer.update()

    def on_item_selection_changed(self):
        for item in self.selectedItems():
            if self.callback:
                self.callback(item.node)
