from typing import TYPE_CHECKING

from compas_viewer.components.widget_tools import LabelWidget

if TYPE_CHECKING:
    from .mainwindow import MainWindow


class SatusBar:
    def __init__(self, parent: "MainWindow", show: bool = True) -> None:
        self.parent = parent
        self.show = show
        self.widget = self.parent.widget.statusBar()
        self.widget.setHidden(not self.show)
        self.label = LabelWidget()
        self.widget.addWidget(self.label(text="Ready..."))
