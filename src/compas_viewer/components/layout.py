from typing import TYPE_CHECKING

from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout

from compas_viewer.components.combobox import ColorComboBox
from compas_viewer.components.double_edit import DoubleEdit
from compas_viewer.components.widget_tools import LabelWidget

if TYPE_CHECKING:
    from compas_viewer import Viewer


def base_layout(coordinates: dict) -> tuple[QVBoxLayout, dict]:
    """
    Generates a layout for editing properties based on provided coordinates and settings.

    Parameters
    ----------
    coordinates : dict
        A dictionary where keys are section names and values are lists of tuples describing the widgets and their parameters.

    Returns
    -------
    tuple[QVBoxLayout, dict]
        A tuple containing the created layout and a dictionary of spin boxes for value adjustment.

    Example
    -------
    >>> coordinates = {
    >>>     "Camera_Target": [("double_edit", "X", 0.0, None, None)],
    >>>     "Camera_Position": [("double_edit", "Y", 1.0, None, None)]
    >>> }
    >>> layout, spin_boxes = base_layout(coordinates)
    """
    layout = QVBoxLayout()

    spin_boxes = {}

    for coord in coordinates:
        sub_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QHBoxLayout()
        label = QLabel(f"{coord}:")
        left_layout.addWidget(label)

        for setting in coordinates[coord]:
            if setting[0] == "double_edit":
                widget = DoubleEdit(*setting[1:])
                right_layout.addWidget(widget)
                spin_boxes[f"{coord}_{setting[1]}"] = widget
            elif setting[0] == "label":
                label_widget = LabelWidget()
                widget = label_widget(setting[1])
                right_layout.addWidget(widget)
            elif setting[0] == "color_combobox":
                widget = ColorComboBox(*setting[1:])
                right_layout.addWidget(widget)

        sub_layout.addLayout(left_layout)
        sub_layout.addLayout(right_layout)

        layout.addLayout(sub_layout)
    return layout, spin_boxes


def create_object_info_layout(viewer: "Viewer") -> tuple[QVBoxLayout, dict]:
    """
    Creates a layout for displaying and editing selected object's properties.

    Parameters
    ----------
    viewer : Viewer
        The viewer containing the scene and objects.

    Returns
    -------
    tuple[QVBoxLayout, dict]
        A tuple containing the created layout and a dictionary of spin boxes for object properties.

    Example
    -------
    >>> layout, spin_boxes = create_object_info_layout(viewer)
    """
    coordinates = {}
    for obj in viewer.scene.objects:
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

    layout, spin_boxes = base_layout(coordinates)

    return layout, spin_boxes


def create_camera_setting_layout(viewer: "Viewer") -> tuple[QVBoxLayout, dict]:
    """
    Creates a layout for editing camera settings including target and position coordinates.

    Parameters
    ----------
    viewer : Viewer
        The viewer containing the camera settings to be modified.

    Returns
    -------
    tuple[QVBoxLayout, dict]
        A tuple containing the created layout and a dictionary of spin boxes for camera settings.

    Example
    -------
    >>> layout, spin_boxes = create_camera_setting_layout(viewer)
    """
    coordinates = {
        "Camera_Target": [
            ("double_edit", "X", viewer.renderer.camera.target.x, None, None),
            ("double_edit", "Y", viewer.renderer.camera.target.y, None, None),
            ("double_edit", "Z", viewer.renderer.camera.target.z, None, None),
        ],
        "Camera_Position": [
            ("double_edit", "X", viewer.renderer.camera.position.x, None, None),
            ("double_edit", "Y", viewer.renderer.camera.position.y, None, None),
            ("double_edit", "Z", viewer.renderer.camera.position.z, None, None),
        ],
    }

    layout, spin_boxes = base_layout(coordinates)

    return layout, spin_boxes
