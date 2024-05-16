from compas_viewer.base import Base
from compas_viewer.components.dialog import CameraSettingsDialog


def openDialog():
    dialog = CameraSettingsDialog()
    dialog.exec()


class MenuBar(Base):
    def __init__(self) -> None:
        self.widget = None

    def lazy_init(self):
        self.widget = self.viewer.ui.window.menuBar()
        filemenu = self.widget.addMenu("Camera")
        filemenu.addAction("Camera_Settings", openDialog)
