from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Literal

from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLayout
from PySide6.QtWidgets import QVBoxLayout

from compas_viewer.components.color import ColorComboBox
from compas_viewer.components.color import ColorDialog
from compas_viewer.components.double_edit import DoubleEdit
from compas_viewer.components.label import LabelWidget
from compas_viewer.components.textedit import TextEdit

if TYPE_CHECKING:
    from compas_viewer import Viewer


class DefaultLayout:
    def __init__(self, layout: QLayout):
        self.layout = layout
        self.layout.setSpacing(0)  # Minimize the spacing between items
        self.layout.setContentsMargins(0, 0, 0, 0)  # Minimize the margins


class SettingLayout:
    """
    A class to generate a dynamic layout for displaying and editing settings of objects or camera in a viewer.

    This class can generate a layout based on the provided items and the type of settings (object or camera).
    It supports various types of widgets including double edits, labels, color dialogs, and text edits.

    Parameters
    ----------
    viewer : Viewer
        The viewer instance containing the scene and objects or camera.
    items : list
        A list of dictionaries where each dictionary represents a section with a title and items describing the widgets and their parameters.
    type : Literal["obj_setting", "camera_setting"]
        The type of settings to generate the layout for. It can be "obj_setting" for object settings or "camera_setting" for camera settings.

    Attributes
    ----------
    layout : QVBoxLayout
        The main layout of the widget.
    widgets : dict
        A dictionary to store the created widgets for easy access.

    Methods
    -------
    generate_layout(viewer, items)
        Generates the layout based on the provided viewer and items.
    set_layout(items, obj)
        Sets the layout for the provided items and object.

    Example
    -------
    >>> items = [
    >>>     {"title": "Name", "items": [{"type": "text_edit", "action": lambda obj: obj.name}]},
    >>>     {"title": "Point_Color", "items": [{"type": "color_dialog", "attr": "pointcolor"}]},
    >>>     {"title": "Line_Color", "items": [{"type": "color_dialog", "attr": "linecolor"}]},
    >>>     {"title": "Face_Color", "items": [{"type": "color_dialog", "attr": "facecolor"}]},
    >>>     {"title": "Line_Width", "items": [{"type": "double_edit", "action": lambda obj: obj.linewidth, "min_val": 0.0, "max_val": 10.0}]},
    >>>     {"title": "Point_Size", "items": [{"type": "double_edit", "action": lambda obj: obj.pointsize, "min_val": 0.0, "max_val": 10.0}]},
    >>>     {"title": "Opacity", "items": [{"type": "double_edit", "action": lambda obj: obj.opacity, "min_val": 0.0, "max_val": 1.0}]},
    >>> ]
    """

    def __init__(
        self,
        viewer: "Viewer",
        items: list[dict],
        type: Literal["obj_setting", "camera_setting"],
    ):
        super().__init__()

        self.viewer = viewer
        self.items = items
        self.type = type

    def generate_layout(self) -> None:
        self.layout = QVBoxLayout()
        self.widgets = {}

        if self.type == "camera_setting":
            self.set_layout(self.items, self.viewer.renderer.camera)

        elif self.type == "obj_setting":
            obj_list = []
            for obj in self.viewer.scene.objects:
                if obj.is_selected:
                    obj_list.append(obj)

            if not obj_list:
                return
            # Only support one item selected per time
            self.set_layout(self.items, obj_list[0])

    def set_layout(self, items: list[dict], obj: Any) -> None:
        for item in items:
            layout_title = item.get("title", "")
            sub_items = item.get("items", None)

            sub_layout = DefaultLayout(QHBoxLayout()).layout
            left_layout = DefaultLayout(QHBoxLayout()).layout
            right_layout = DefaultLayout(QHBoxLayout()).layout

            label = QLabel(f"{layout_title}:")
            left_layout.addWidget(label)

            for sub_item in sub_items:
                sub_title: str = sub_item.get("title", None)
                type: str = sub_item.get("type", None)
                action: Callable[[Any], Any] = sub_item.get("action", None)
                attr: str = sub_item.get("attr", None)
                min_val: float = sub_item.get("min_val", None)
                max_val: float = sub_item.get("max_val", None)

                if type == "double_edit":
                    value = action(obj)
                    widget = DoubleEdit(title=sub_title, value=value, min_val=min_val, max_val=max_val)
                elif type == "label":
                    text = action(obj)
                    widget = LabelWidget(text=text, alignment="center")
                elif type == "color_combobox":
                    widget = ColorComboBox(obj=obj, attr=attr)
                elif type == "text_edit":
                    text = str(action(obj))
                    widget = TextEdit(text=text)
                elif type == "color_dialog":
                    widget = ColorDialog(obj=obj, attr=attr)

                if sub_title is None:
                    widget_name = f"{layout_title}_{type}"
                else:
                    widget_name = f"{layout_title}_{sub_title}_{type}"

                self.widgets[widget_name] = widget
                right_layout.addWidget(widget)

            sub_layout.addLayout(left_layout)
            sub_layout.addLayout(right_layout)

            self.layout.addLayout(sub_layout)
