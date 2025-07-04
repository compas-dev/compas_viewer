from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLayout

if TYPE_CHECKING:
    from .ui import UI


class Container:
    def __init__(self, ui: "UI", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = ui
        self.widget: QLayout = None
        self.children = []

    def add(self, ui_element):
        self.children.append(ui_element)
        self.widget.addWidget(ui_element.widget)

    def remove(self, ui_element):
        self.children.remove(ui_element)
        self.widget.removeWidget(ui_element.widget)

    @property
    def show(self):
        return self.widget.isVisible()

    @show.setter
    def show(self, value: bool):
        self.widget.setVisible(value)

    def update(self):
        self.widget.update()

        # TODO: Avoid double updates
        for child in self.children:
            child.update()
