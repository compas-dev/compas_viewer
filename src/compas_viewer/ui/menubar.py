from PySide6.QtGui import QAction

from compas_viewer.base import Base
from compas_viewer.components.combobox import ViewModeAction
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
        camera_filemenu = self.widget.addMenu("Camera")
        viewmode_menu = camera_filemenu.addMenu("Viewmode")
        viewmode_menu.addAction(self.viewmode_action("perspective"))
        viewmode_menu.addAction(self.viewmode_action("top"))
        viewmode_menu.addAction(self.viewmode_action("front"))
        viewmode_menu.addAction(self.viewmode_action("right"))

    def viewmode_action(self, mode: str):
        action = QAction(mode, self.widget)
        action.triggered.connect(lambda check=False, mode=mode: ViewModeAction().change_view(mode))
        return action
