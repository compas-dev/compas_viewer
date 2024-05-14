from typing import TYPE_CHECKING

from compas_viewer.base import Base

if TYPE_CHECKING:
    pass


def new_file():
    print("new file...")


class MenuBar(Base):
    def __init__(self) -> None:
        self.widget = None

    def lazy_init(self):
        self.widget = self.viewer.ui.window.menuBar()
        filemenu = self.widget.addMenu("File")
        filemenu.addAction("New File...", new_file)
