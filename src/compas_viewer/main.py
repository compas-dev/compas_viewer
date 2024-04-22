
import sys
from PySide6.QtWidgets import QApplication
from compas_viewer.config import Config
from compas_viewer.scene.scene import ViewerScene
from compas_viewer.ui.ui import UI

class Viewer:
    def __init__(self) -> None:
        self.app = QApplication(sys.argv)
        self.config = Config()
        self.ui = UI(self)
        self.scene = ViewerScene(self, name="ViewerScene", context="Viewer")
        self.is_started = False

    def init(self):
        self.ui.init()

    def show(self):
        self.ui.init()
        self.ui.show()
        self.is_started = True
        self.app.exec()


if __name__ == "__main__":
    viewer = Viewer()
    viewer.show()
