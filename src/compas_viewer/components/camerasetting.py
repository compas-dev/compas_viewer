from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout

from compas_viewer.base import Base
from compas_viewer.components.layout import SettingLayout


class CameraSettingsDialog(QDialog, Base):
    """
    A dialog for displaying and updating camera settings in Qt applications.
    This dialog allows users to modify the camera's target and position and
    applies these changes dynamically.

    Attributes
    ----------
    layout : QVBoxLayout
        The layout of the dialog.
    spin_boxes : dict
        Dictionary containing spin boxes for adjusting camera settings.
    update_button : QPushButton
        Button to apply changes to the camera settings.
    camera : Camera
        The camera object from the viewer's renderer.

    Methods
    -------
    update()
        Updates the camera's target and position and closes the dialog.

    Example
    -------
    >>> dialog = CameraSettingsDialog()
    >>> dialog.exec()
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Camera Settings")

        self.layout = QVBoxLayout(self)
        items = [
            {
                "title": "Camera_Target",
                "items": [
                    {"type": "double_edit", "title": "X", "action": lambda camera: camera.target.x, "min_val": None, "max_val": None},
                    {"type": "double_edit", "title": "Y", "action": lambda camera: camera.target.y, "min_val": None, "max_val": None},
                    {"type": "double_edit", "title": "Z", "action": lambda camera: camera.target.z, "min_val": None, "max_val": None},
                ],
            },
            {
                "title": "Camera_Position",
                "items": [
                    {"type": "double_edit", "title": "X", "action": lambda camera: camera.position.x, "min_val": None, "max_val": None},
                    {"type": "double_edit", "title": "Y", "action": lambda camera: camera.position.y, "min_val": None, "max_val": None},
                    {"type": "double_edit", "title": "Z", "action": lambda camera: camera.position.z, "min_val": None, "max_val": None},
                ],
            },
        ]
        self.setting_layout = SettingLayout(viewer=self.viewer, items=items, type="camera_setting")

        self.layout.addLayout(self.setting_layout.layout)

        self.update_button = QPushButton("Update Camera", self)
        self.update_button.clicked.connect(self.update)
        self.layout.addWidget(self.update_button)

    def update(self) -> None:
        self.viewer.renderer.camera.target.set(
            self.setting_layout.widgets["Camera_Target_X_double_edit"].spinbox.value(),
            self.setting_layout.widgets["Camera_Target_Y_double_edit"].spinbox.value(),
            self.setting_layout.widgets["Camera_Target_Z_double_edit"].spinbox.value(),
        )
        self.viewer.renderer.camera.position.set(
            self.setting_layout.widgets["Camera_Position_X_double_edit"].spinbox.value(),
            self.setting_layout.widgets["Camera_Position_Y_double_edit"].spinbox.value(),
            self.setting_layout.widgets["Camera_Position_Z_double_edit"].spinbox.value(),
        )
        self.accept()
