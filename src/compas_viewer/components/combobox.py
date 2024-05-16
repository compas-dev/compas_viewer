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
        for text, data in items:
            self.addItem(text, data)


class ViewComboBox(QWidget, Base):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        view_options = [("Perspective", "perspective"), ("Top", "top"), ("Front", "front"), ("Right", "right"), ("Left", "left")]
        self.view_selector = ComboBox(view_options, self.change_view)
        self.layout.addWidget(self.view_selector)

    def change_view(self, view):
        """
        Change the view of the renderer based on the selected option.

        :param view: The user data associated with the selected item
        """
        if view == "perspective":
            self.viewer.renderer.viewmode = "perspective"
        elif view == "top":
            self.viewer.renderer.viewmode = "top"
        elif view == "front":
            self.viewer.renderer.viewmode = "front"
        elif view == "right":
            self.viewer.renderer.viewmode = "right"
        elif view == "left":
            self.viewer.renderer.viewmode = "left"
