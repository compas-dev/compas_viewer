from typing import Any

from compas.datastructures import Tree
from PySide6.QtWidgets import QTreeWidget
from PySide6.QtWidgets import QTreeWidgetItem


class Treeform(QTreeWidget):
    """
    Class for displaying tree-like data.
    Treeform is an abstract class that could be placed in either the viewport or the sidedock.

    Parameters
    ----------
    #TODO

    """

    def __init__(
        self,
        data: Tree,
        columns: list[str] = ["name", "value"],
        column_editable: list[bool] = [False, False],
        show_headers: bool = True,
        striped_rows: bool = False,
    ):
        super().__init__()
        self.columns = columns
        self.column_editable = column_editable
        if len(columns) != len(column_editable):
            raise ValueError("columns and column_editable must have the same length")

        self.setHeaderLabels(self.columns)
        self.setHeaderHidden(not show_headers)
        self.striped_rows = striped_rows

        self.data = data
        self.tree = Tree()

    #     self.update()

    # @property
    # def data(self):
    #     return self.data

    # @data.setter
    # def data(self, objects: Tree):
    #     for node in self.data.nodes:
    #         item = QTreeWidgetItem(strings=[node.data.get(self.columns[0]), node.data.get(self.columns[1])])
    #         self.tree.add()

    #     self._objects = objects
    #     self.update()

    # def update(self):
    #     self.clear()
    #     self.items = Tree()

    #     # item.setExpanded(True)
    #     self.resizeColumnToContents(0)
