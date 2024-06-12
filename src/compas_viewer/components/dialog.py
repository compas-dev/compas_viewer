from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout

from compas.colors import Color
from compas_viewer.base import Base
from compas_viewer.components.layout import create_camera_setting_layout
from compas_viewer.components.layout import create_object_info_layout


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

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Camera Settings")

        self.layout = QVBoxLayout(self)

        camera_setting_layout, self.spin_boxes = create_camera_setting_layout(self.viewer)
        self.layout.addLayout(camera_setting_layout)

        # Update button
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
        self.accept()  # Close the dialog


class ObjectInfoDialog(QDialog, Base):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Object Settings")
        self.layout = QVBoxLayout(self)

        object_info_layout, self.spin_boxes = create_object_info_layout(self.viewer)
        self.layout.addLayout(object_info_layout)

        # Update button
        self.update_button = QPushButton("Update Object", self)
        self.update_button.clicked.connect(self.update)
        self.layout.addWidget(self.update_button)

    def update(self) -> None:
        for obj in self.viewer.scene.objects:
            if obj.is_selected:
                obj.linewidth = self.spin_boxes["Line_Width_"].spinbox.value()
                obj.pointsize = self.spin_boxes["Point_Size_"].spinbox.value()
                obj.opacity = self.spin_boxes["Opacity_"].spinbox.value()
                obj.color = Color(
                    self.spin_boxes["Color_R"].spinbox.value(),
                    self.spin_boxes["Color_G"].spinbox.value(),
                    self.spin_boxes["Color_B"].spinbox.value(),
                )

        self.accept()  # Close the dialog
