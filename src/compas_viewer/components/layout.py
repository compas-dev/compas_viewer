from typing import Literal

from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLayout
from PySide6.QtWidgets import QVBoxLayout

from compas_viewer.components.color import ColorButton
from compas_viewer.components.color import ColorComboBox
from compas_viewer.components.double_edit import DoubleEdit
from compas_viewer.components.label import LabelWidget
from compas_viewer.components.textedit import TextEdit


class DefaultLayout:
    def __init__(self, layout: QLayout):
        self.layout = layout
        self.layout.setSpacing(0)  # Minimize the spacing between items
        self.layout.setContentsMargins(0, 0, 0, 0)  # Minimize the margins

    def get_layout(self) -> QLayout:
        return self.layout


class SettingLayout:
    def __init__(self, viewer=None, items=None, type: Literal["obj_setting", "camera_setting"] = None):
        super().__init__()
        self.viewer = viewer
        self.type = type
        self.layout = QVBoxLayout()
        self.widgets = {}
        if viewer:
            self.generate_layout(viewer, items)

    def generate_layout(self, viewer, items):
        obj_list = []
        if self.type == "camera_setting":
            self.set_layout(items, self.viewer.renderer.camera)

        elif self.type == "obj_setting":
            obj_list = []
            for obj in viewer.scene.objects:
                if obj.is_selected:
                    obj_list.append(obj)

            if obj_list:
                # Only support one item selected per time
                self.set_layout(items, obj_list[0])

    def set_layout(self, items: list, obj):
        self.layout = QVBoxLayout()

        for item in items:
            l_title = item.get("title", "")
            sub_items = item.get("items", None)

            sub_layout = DefaultLayout(QHBoxLayout()).get_layout()
            left_layout = DefaultLayout(QHBoxLayout()).get_layout()
            right_layout = DefaultLayout(QHBoxLayout()).get_layout()

            label = QLabel(f"{l_title}:")
            left_layout.addWidget(label)

            for sub_item in sub_items:
                s_title = sub_item.get("title", None)
                type = sub_item.get("type", None)
                action = sub_item.get("action", None)
                attr = sub_item.get("attr", None)
                min_val = sub_item.get("min_val", None)
                max_val = sub_item.get("max_val", None)

                if type == "double_edit":
                    value = action(obj)
                    widget = DoubleEdit(title=s_title, value=value, min_val=min_val, max_val=max_val)
                    right_layout.addWidget(widget)
                    if s_title is None:
                        widget_name = f"{l_title}_{type}"
                    else:
                        widget_name = f"{l_title}_{s_title}_{type}"
                    self.widgets[widget_name] = widget
                elif type == "label":
                    text = action(obj)
                    widget = LabelWidget(text=text, alignment="center")
                    right_layout.addWidget(widget)
                elif type == "color_combobox":
                    widget = ColorComboBox(obj=obj, attr=attr)
                    right_layout.addWidget(widget)
                elif type == "text_edit":
                    text = str(action(obj))
                    widget = TextEdit(text=text)
                    right_layout.addWidget(widget)
                    self.widgets[f"{l_title}_{type}"] = widget
                elif type == "color_dialog":
                    widget = ColorButton(obj=obj, attr=attr)
                    right_layout.addWidget(widget)

            sub_layout.addLayout(left_layout)
            sub_layout.addLayout(right_layout)

            self.layout.addLayout(sub_layout)
