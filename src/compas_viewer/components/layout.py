from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout

from compas_viewer.components.combobox import ColorComboBox
from compas_viewer.components.double_edit import DoubleEdit
from compas_viewer.components.label import LabelWidget


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
                widget = LabelWidget(text=setting[1], alignment="right")
                right_layout.addWidget(widget)
            elif setting[0] == "color_combobox":
                widget = ColorComboBox(*setting[1:])
                right_layout.addWidget(widget)

        sub_layout.addLayout(left_layout)
        sub_layout.addLayout(right_layout)

        layout.addLayout(sub_layout)
    return (layout, spin_boxes)
