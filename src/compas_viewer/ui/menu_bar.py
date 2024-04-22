from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ui import UI

def new_file():
    print("new file...")

class MenuBar:
    def __init__(self, ui: "UI") -> None:
        self.ui = ui
        self.window = self.ui.window
        self.widget = self.window.menuBar()

        filemenu = self.widget.addMenu("File")
        filemenu.addAction("New File...", new_file)
