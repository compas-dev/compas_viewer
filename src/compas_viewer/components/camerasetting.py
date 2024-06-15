from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout

from compas_viewer.base import Base
from compas_viewer.components.layout import base_layout


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
        self.camera = self.viewer.renderer.camera
        items = [
            {
                "title": "Camera_Target",
                "items": [
                    {"type": "double_edit", "title": "X", "value": self.camera.target.x, "min_val": None, "max_val": None},
                    {"type": "double_edit", "title": "Y", "value": self.camera.target.y, "min_val": None, "max_val": None},
                    {"type": "double_edit", "title": "Z", "value": self.camera.target.z, "min_val": None, "max_val": None},
                ],
            },
            {
                "title": "Camera_Position",
                "items": [
                    {"type": "double_edit", "title": "X", "value": self.camera.position.x, "min_val": None, "max_val": None},
                    {"type": "double_edit", "title": "Y", "value": self.camera.position.y, "min_val": None, "max_val": None},
                    {"type": "double_edit", "title": "Z", "value": self.camera.position.z, "min_val": None, "max_val": None},
                ],
            },
        ]

        camera_setting_layout, self.spin_boxes = base_layout(items)

        self.layout.addLayout(camera_setting_layout)

        self.update_button = QPushButton("Update Camera", self)
        self.update_button.clicked.connect(self.update)
        self.layout.addWidget(self.update_button)

    def update(self) -> None:
        self.viewer.renderer.camera.target.set(
            self.spin_boxes["Camera_Target_X"].spinbox.value(),
            self.spin_boxes["Camera_Target_Y"].spinbox.value(),
            self.spin_boxes["Camera_Target_Z"].spinbox.value(),
        )
        self.viewer.renderer.camera.position.set(
            self.spin_boxes["Camera_Position_X"].spinbox.value(),
            self.spin_boxes["Camera_Position_Y"].spinbox.value(),
            self.spin_boxes["Camera_Position_Z"].spinbox.value(),
        )
        self.accept()
