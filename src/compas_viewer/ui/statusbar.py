from typing import TYPE_CHECKING

from compas_viewer.components.widget_tools import LabelWidget

if TYPE_CHECKING:
    from .ui import UI


class SatusBar:
    def __init__(self, parent: "UI", show: bool = True) -> None:
        self.parent = parent
        self.widget = self.parent.window.widget.statusBar()
        self.widget.setVisible(show)
        self.label = LabelWidget()
        self.widget.addWidget(self.label(text="Ready..."))

    @property
    def show(self):
        return self.widget.isVisible()

    @show.setter
    def show(self, value: bool):
        self.widget.setVisible(value)
