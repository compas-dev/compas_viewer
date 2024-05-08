from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def new_file():
    print("new file...")


class MenuBar:
    def __init__(self) -> None:
        self.widget = None

    @property
    def viewer(self):
        from compas_viewer.viewer import Viewer

        return Viewer()

    def setup_menu(self):
        self.widget = self.viewer.ui.window.menuBar()
        filemenu = self.widget.addMenu("File")
        filemenu.addAction("New File...", new_file)
