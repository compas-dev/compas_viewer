from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout

from compas_viewer.base import Base
from compas_viewer.components.layout import base_layout


def object_setting_layout(viewer):
    """
    Generates a layout for displaying object information based on the provided object.

    Parameters
    ----------
    obj : object
        The object for which to display information.

    Returns
    -------
    QVBoxLayout
        The layout for displaying object information.

    Example
    -------
    >>> layout = object_info_layout(obj)
    """

    coordinates = {}
    for obj in viewer.scene.objects:
        if obj.is_selected:
            new_coordinates = {
                "Name": [("label", str(obj.name))],
                "Parent": [("label", str(obj.parent))],
                # TODO: check _color attr ("double_edit", "G", obj.linecolor[0].g, 0, 1),
                "Point_Color": [("color_combobox", obj, "pointcolor")],
                "Line_Color": [("color_combobox", obj, "linecolor")],
                "Face_Color": [("color_combobox", obj, "facecolor")],
                "Line_Width": [("double_edit", "", obj.linewidth, 0.0, 10.0)],
                "Point_Size": [("double_edit", "", obj.pointsize, 0.0, 10.0)],
                "Opacity": [("double_edit", "", obj.opacity, 0.0, 1.0)],
            }
            coordinates.update(new_coordinates)

    object_info_layout, spin_boxes = base_layout(coordinates)

    return object_info_layout, spin_boxes


class ObjectSettingDialog(QDialog, Base):
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

        obj_setting_layout, self.spin_boxes = object_setting_layout(self.viewer)
        self.layout.addLayout(obj_setting_layout)

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
