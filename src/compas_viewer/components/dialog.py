from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout

from compas_viewer.base import Base
from compas_viewer.components.layout import create_camera_setting_layout
from compas_viewer.components.layout import create_object_info_layout


class CameraSettingsDialog(QDialog, Base):
    """
    A dialog for displaying and updating camera settings in Qt applications.
    This dialog allows users to modify the camera's target and position,
    and applies these changes dynamically.

    Attributes
    ----------
    layout : QVBoxLayout
        The layout of the dialog.
    spin_boxes : dict
        Dictionary containing spin boxes for adjusting camera settings.
    update_button : QPushButton
        Button to apply changes to the camera settings.

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

        camera_setting_layout, self.spin_boxes = create_camera_setting_layout(self.viewer)
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


class ObjectInfoDialog(QDialog, Base):
    """
    A dialog for displaying and updating object settings in Qt applications.
    This dialog allows users to modify object properties such as line width, point size, and opacity,
    and applies these changes dynamically.

    Attributes
    ----------
    layout : QVBoxLayout
        The layout of the dialog.
    spin_boxes : dict
        Dictionary containing spin boxes for adjusting object properties.
    update_button : QPushButton
        Button to apply changes to the selected objects.

    Methods
    -------
    update()
        Updates the properties of selected objects and closes the dialog.

    Example
    -------
    >>> dialog = ObjectInfoDialog()
    >>> dialog.exec()
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Object Settings")
        self.layout = QVBoxLayout(self)

        object_info_layout, self.spin_boxes = create_object_info_layout(self.viewer)
        self.layout.addLayout(object_info_layout)

        self.update_button = QPushButton("Update Object", self)
        self.update_button.clicked.connect(self.update)
        self.layout.addWidget(self.update_button)

    def update(self) -> None:
        for obj in self.viewer.scene.objects:
            if obj.is_selected:
                obj.linewidth = self.spin_boxes["Line_Width_"].spinbox.value()
                obj.pointsize = self.spin_boxes["Point_Size_"].spinbox.value()
                obj.opacity = self.spin_boxes["Opacity_"].spinbox.value()
                obj.update()

        self.accept()
