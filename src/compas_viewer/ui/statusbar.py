from typing import TYPE_CHECKING

from compas_viewer.components.widget_tools import LabelWidget

if TYPE_CHECKING:
    from .ui import UI


class SatusBar:
    def __init__(self, ui: "UI", show: bool = True) -> None:
        self.ui = ui
        self.widget = self.ui.window.widget.statusBar()
        self.label = LabelWidget()
        self.widget.addWidget(self.label(text="Ready..."))
        self.show = show

    @property
    def show(self):
        return self.widget.isVisible()

    @show.setter
    def show(self, value: bool):
        if value:
            self.widget.setVisible(True)
        elif not value:
            self.widget.setHidden(True)
