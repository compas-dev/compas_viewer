from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout

from compas_viewer.base import Base
from compas_viewer.components.double_edit import DoubleEdit


class CameraSettingsDialog(QDialog, Base):
    """
    Dialog for adjusting camera settings in a graphical user interface.

    This dialog allows users to dynamically modify the camera's position and target coordinates
    through the use of spin boxes for each coordinate axis (X, Y, Z).

    Attributes
    ----------
    layout : QVBoxLayout
        The layout for arranging widgets vertically within the dialog.
    spin_boxes : dict
        Stores references to spin box widgets for easy access when updating camera settings.
    update_button : QPushButton
        Button for applying the updated camera settings and closing the dialog.

    Notes
    -----
    This class assumes that there is an existing viewer with a renderer and camera attribute.
    It should be used where these components are already established and accessible.

    Examples
    --------
    Assuming `viewer` is an instance with a renderer and camera attributes:

    >>> dialog = CameraSettingsDialog()
    >>> dialog.exec_()  # Executing the dialog to allow user interaction

    References
    ----------
    * https://doc.qt.io/qt-6/qdialog.html
    * https://doc.qt.io/qt-6/qlayout.html
    * https://doc.qt.io/qt-6/qpushbutton.html

    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Settings")

        # Create layout for spin boxes
        self.layout = QVBoxLayout(self)
        self.spin_boxes = {}
        current_camera = self.viewer.renderer.camera

        coordinates = {
            "Camera_Target": [("X", current_camera.target.x, 0, 10000), ("Y", current_camera.target.y, 0, 10000), ("Z", current_camera.target.z, 0, 10000)],
            "Camera_Position": [("X", current_camera.position.x, 1, 10000), ("Y", current_camera.position.y, 1, 10000), ("Z", current_camera.position.z, 1, 10000)],
        }

        for coord in coordinates:
            spin_box_layout = QHBoxLayout()
            label = QLabel(f"{coord}:", self)
            spin_box_layout.addWidget(label)

            for setting in coordinates[coord]:
                widget = DoubleEdit(*setting)
                spin_box_layout.addWidget(widget)
                self.spin_boxes[coord + "_" + setting[0]] = widget

            self.layout.addLayout(spin_box_layout)

        # Update button
        self.update_button = QPushButton("Update Camera", self)
        self.update_button.clicked.connect(self.updateCameraTarget)
        self.layout.addWidget(self.update_button)

    def updateCameraTarget(self):
        self.viewer.renderer.camera.target = [
            self.spin_boxes["Camera_Target_X"].spinbox.value(),
            self.spin_boxes["Camera_Target_Y"].spinbox.value(),
            self.spin_boxes["Camera_Target_Z"].spinbox.value(),
        ]
        self.viewer.renderer.camera.position = [
            self.spin_boxes["Camera_Position_X"].spinbox.value(),
            self.spin_boxes["Camera_Position_Y"].spinbox.value(),
            self.spin_boxes["Camera_Position_Z"].spinbox.value(),
        ]
        self.accept()  # Close the dialog
