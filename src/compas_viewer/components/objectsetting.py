from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas_viewer.base import Base
from compas_viewer.components.layout import base_layout

if TYPE_CHECKING:
    from compas_viewer import Viewer


def object_setting_layout(viewer: "Viewer"):
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
    status = False
    coordinates = {}
    for obj in viewer.scene.objects:
        if obj.is_selected:
            status = True
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

    if not status:
        return None

    return base_layout(coordinates)


class ObjectSetting(QWidget):
    """
    A QWidget to manage the settings of objects in the viewer.

    Parameters
    ----------
    viewer : Viewer
        The viewer instance containing the objects.

    Attributes
    ----------
    viewer : Viewer
        The viewer instance.
    layout : QVBoxLayout
        The main layout for the widget.
    update_button : QPushButton
        The button to trigger the object update.
    spin_boxes : dict
        Dictionary to hold spin boxes for object properties.

    Methods
    -------
    clear_layout(layout)
        Clears all widgets and sub-layouts from the given layout.
    update()
        Updates the layout with the latest object settings.
    obj_update()
        Applies the settings from spin boxes to the selected objects.
    """

    update_requested = Signal()

    def __init__(self, viewer: "Viewer"):
        super().__init__()
        self.viewer = viewer
        self.layout = QVBoxLayout(self)
        self.spin_boxes = {}

    def clear_layout(self, layout):
        """Clear all widgets from the layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    self.clear_layout(sub_layout)

    def update(self):
        """Update the layout with the latest object settings."""
        self.clear_layout(self.layout)
        output = object_setting_layout(self.viewer)

        if output is not None:
            text = "Update Object"
            obj_setting_layout, self.spin_boxes = output
            self.layout.addLayout(obj_setting_layout)
        else:
            text = "No object selected."

        self.update_button = QPushButton(text, self)
        self.update_button.clicked.connect(self.obj_update)
        self.layout.addWidget(self.update_button)

    def obj_update(self):
        """Apply the settings from spin boxes to the selected objects."""
        for obj in self.viewer.scene.objects:
            if obj.is_selected:
                obj.linewidth = self.spin_boxes["Line_Width_"].spinbox.value()
                obj.pointsize = self.spin_boxes["Point_Size_"].spinbox.value()
                obj.opacity = self.spin_boxes["Opacity_"].spinbox.value()
                obj.update()


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
        output = object_setting_layout(self.viewer)

        if output is not None:
            text = "Update Object"
            obj_setting_layout, self.spin_boxes = output
            self.layout.addLayout(obj_setting_layout)
        else:
            text = "No object selected."

        self.update_button = QPushButton(text, self)
        self.update_button.clicked.connect(self.obj_update)
        self.layout.addWidget(self.update_button)

    def obj_update(self) -> None:
        for obj in self.viewer.scene.objects:
            if obj.is_selected:
                obj.linewidth = self.spin_boxes["Line_Width_"].spinbox.value()
                obj.pointsize = self.spin_boxes["Point_Size_"].spinbox.value()
                obj.opacity = self.spin_boxes["Opacity_"].spinbox.value()
                obj.update()

        self.accept()
