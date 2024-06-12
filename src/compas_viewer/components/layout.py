from typing import Any
from typing import Dict

from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout

from compas_viewer.components.double_edit import DoubleEdit

COLORS = []


def create_object_info_layout(viewer) -> Dict[str, Any]:
    layout = QVBoxLayout()
    spin_boxes = {}
    coordinates = {}
    for obj in viewer.scene.objects:
        if obj.is_selected:
            new_coordinates = {
                "Color": [
                    ("R", obj.color.r, 0, 1),
                    ("G", obj.color.g, 0, 1),
                    ("B", obj.color.b, 0, 1),
                ],
                "Line_Width": [("", obj.linewidth, 0.0, 10.0)],
                "Point_Size": [("", obj.pointsize, 0.0, 10.0)],
                "Opacity": [("", obj.opacity, 0.0, 1.0)],
            }
            coordinates.update(new_coordinates)

    for coord in coordinates:
        spin_box_layout = QHBoxLayout()
        label = QLabel(f"{coord}:")
        spin_box_layout.addWidget(label)

        for setting in coordinates[coord]:
            if len(setting) == 4:
                widget = DoubleEdit(*setting)
                spin_box_layout.addWidget(widget)
                spin_boxes[f"{coord}_{setting[0]}"] = widget

        layout.addLayout(spin_box_layout)

    return layout, spin_boxes


def create_camera_setting_layout(viewer) -> Dict[str, Any]:
    layout = QVBoxLayout()
    spin_boxes = {}

    coordinates = {
        "Camera_Target": [
            ("X", viewer.renderer.camera.target.x, None, None),
            ("Y", viewer.renderer.camera.target.y, None, None),
            ("Z", viewer.renderer.camera.target.z, None, None),
        ],
        "Camera_Position": [
            ("X", viewer.renderer.camera.position.x, None, None),
            ("Y", viewer.renderer.camera.position.y, None, None),
            ("Z", viewer.renderer.camera.position.z, None, None),
        ],
    }

    for coord in coordinates:
        spin_box_layout = QHBoxLayout()
        label = QLabel(f"{coord}:")
        spin_box_layout.addWidget(label)

        for setting in coordinates[coord]:
            widget = DoubleEdit(*setting)
            spin_box_layout.addWidget(widget)
            spin_boxes[coord + "_" + setting[0]] = widget

        layout.addLayout(spin_box_layout)

    return layout, spin_boxes
