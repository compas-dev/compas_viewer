from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout

from compas_viewer.components.combobox import ColorComboBox
from compas_viewer.components.double_edit import DoubleEdit
from compas_viewer.components.label import LabelWidget


def base_layout(items: list) -> tuple[QVBoxLayout, dict]:
    """
    Generates a layout for editing properties based on provided items and settings.

    Parameters
    ----------
    items : list
        A list of dictionaries where each dictionary represents a section with a title and items describing the widgets and their parameters.

    Returns
    -------
    tuple[QVBoxLayout, dict]
        A tuple containing the created layout and a dictionary of spin boxes for value adjustment.

    Example
    -------
    >>> items = [
    >>>     {"title": "Camera_Target", "items": [{"type": "double_edit", "title": "X", "value": 0.0, "min_val": 0.0, "max_val": 1.0}]},
    >>>     {"title": "Camera_Position", "items": [{"type": "double_edit", "title": "Y", "value": 1.0, "min_val": 0.0, "max_val": 1.0}]}
    >>> ]
    >>> layout, spin_boxes = base_layout(items)
    """
    layout = QVBoxLayout()

    spin_boxes = {}

    for item in items:
        l_title = item.get("title", "")
        sub_items = item.get("items", None)

        sub_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QHBoxLayout()

        label = QLabel(f"{l_title}:")
        left_layout.addWidget(label)

        for sub_item in sub_items:
            r_title = sub_item.get("title", "")
            type = sub_item.get("type", None)
            text = sub_item.get("text", "")
            obj = sub_item.get("obj", None)
            attr = sub_item.get("attr", None)
            value = sub_item.get("value", None)
            min_val = sub_item.get("min_val", None)
            max_val = sub_item.get("max_val", None)

            if type == "double_edit":
                widget = DoubleEdit(title=r_title, value=value, min_val=min_val, max_val=max_val)
                right_layout.addWidget(widget)
                spin_boxes[f"{l_title}_{r_title}"] = widget
            elif type == "label":
                widget = LabelWidget(text=text, alignment="right")
                right_layout.addWidget(widget)
            elif type == "color_combobox":
                widget = ColorComboBox(obj=obj, attr=attr)
                right_layout.addWidget(widget)

        sub_layout.addLayout(left_layout)
        sub_layout.addLayout(right_layout)

        layout.addLayout(sub_layout)
    return (layout, spin_boxes)
