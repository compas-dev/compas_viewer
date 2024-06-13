from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout

from compas_viewer.base import Base
from compas_viewer.components.layout import base_layout


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

        coordinates = {
            "Camera_Target": [
                ("double_edit", "X", self.viewer.renderer.camera.target.x, None, None),
                ("double_edit", "Y", self.viewer.renderer.camera.target.y, None, None),
                ("double_edit", "Z", self.viewer.renderer.camera.target.z, None, None),
            ],
            "Camera_Position": [
                ("double_edit", "X", self.viewer.renderer.camera.position.x, None, None),
                ("double_edit", "Y", self.viewer.renderer.camera.position.y, None, None),
                ("double_edit", "Z", self.viewer.renderer.camera.position.z, None, None),
            ],
        }

        camera_setting_layout, self.spin_boxes = base_layout(coordinates)

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

        coordinates = {}
        for obj in self.viewer.scene.objects:
            if obj.is_selected:
                new_coordinates = {
                    "Name": [
                        ("label", str(obj.name)),
                    ],
                    "Parent": [
                        ("label", str(obj.parent)),
                    ],
                    "Show": [
                        ("buttom", obj.show),
                    ],
                    # TODO: check _color attr
                    "Point_Color": [
                        ("color_combobox", obj, "pointcolor"),
                    ],
                    "Line_Color": [
                        ("color_combobox", obj, "linecolor"),
                        # ("double_edit", "G", obj.linecolor[0].g, 0, 1),
                    ],
                    "Face_Color": [
                        ("color_combobox", obj, "facecolor"),
                    ],
                    "Line_Width": [("double_edit", "", obj.linewidth, 0.0, 10.0)],
                    "Point_Size": [("double_edit", "", obj.pointsize, 0.0, 10.0)],
                    "Opacity": [("double_edit", "", obj.opacity, 0.0, 1.0)],
                }
                coordinates.update(new_coordinates)

        object_info_layout, self.spin_boxes = base_layout(coordinates)

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
