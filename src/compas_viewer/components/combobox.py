from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas_viewer.base import Base


class ComboBox(QComboBox):
    def __init__(self, items, change_callback):
        super().__init__()
        self.populate(items)
        self.currentIndexChanged.connect(lambda index: change_callback(self.itemData(index)))

    def populate(self, items):
        """
        Populate the combo box with items.

        :param items: List of tuples, each containing the display text and user data
        """
        for item in items:
            self.addItem(item, item)


class ViewModeAction(QWidget, Base):
    def __init__(self):
        super().__init__()
        self.view_options = ["perspective", "top", "front", "right"]

    def combobox(self):
        self.layout = QVBoxLayout(self)
        self.view_selector = ComboBox(self.view_options, self.change_view)
        self.layout.addWidget(self.view_selector)
        return self

    def change_view(self, mode):
        self.viewer.renderer.view = mode
