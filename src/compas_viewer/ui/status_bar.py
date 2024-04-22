from typing import TYPE_CHECKING
from PySide6 import QtWidgets
from compas_viewer.components.label_factory import LabelFactory

if TYPE_CHECKING:
    from .ui import UI

class SatusBar:
    def __init__(self, ui: "UI") -> None:
        self.ui = ui
        self.config = ui.viewer.config.ui.statusbar
        self.window = self.ui.window
        self.widget = self.window.statusBar()
        self.label = LabelFactory()

        self.init_status_bar()

    def init_status_bar(self) -> None:
        self.widget.setHidden(not self.config.show)
        self.widget.addWidget(self.label.set_text(text="Ready..."))