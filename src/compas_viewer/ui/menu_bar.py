from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ui import UI

def new_file():
    print("new file...")

class MenuBar:
    def __init__(self) -> None:
        self.widget = None
    
    @property
    def viewer(self):
        from compas_viewer.main import Viewer
        return Viewer()
    
    def setup_menu(self):
        self.widget = self.viewer.ui.window.menuBar()
        filemenu = self.widget.addMenu("File")
        filemenu.addAction("New File...", new_file)

