from compas_viewer.base import Base
from compas_viewer.components.combobox import ViewModeAction
from compas_viewer.components.button import Button
from compas_viewer.components.dialog import CameraSettingsDialog


def openDialog():
    dialog = CameraSettingsDialog()
    dialog.exec()


class ToolBar(Base):
    def __init__(self) -> None:
        self.widget = None

    def lazy_init(self):
        self.widget = self.viewer.ui.window.addToolBar("Tools")
        self.widget.setMovable(False)
        self.widget.setObjectName("Tools")
        self.widget.setHidden(not self.viewer.config.ui.toolbar.show)
        self.widget.addWidget(Button("camera_info.svg", "Camera_Settings", openDialog))
        self.widget.addWidget(ViewModeAction().combobox())
