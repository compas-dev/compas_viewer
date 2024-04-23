import pathlib
from typing import TYPE_CHECKING
from compas_viewer.components.button_factory import ButtonFactory

if TYPE_CHECKING:
    from .ui import UI

def test_action() -> None:
    print("test action...")

class ToolBar:
    def __init__(self, ui: "UI") -> None:
        self.ui = ui
        self.config = ui.viewer.config.ui.toolbar
        self.window = self.ui.window
        self.widget = self.window.addToolBar("Tools")

        self.init_toolbar()

    def init_toolbar(self) -> None:
        self.widget.setMovable(False)
        self.widget.setObjectName("Tools")
        self.widget.setHidden(not self.config.show)
        self.widget.addWidget(ButtonFactory("zoom_selected.svg", "zoom", test_action()))