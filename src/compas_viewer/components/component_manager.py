from PySide6.QtWidgets import QWidget

from .default_component_factory import ViewerSetting
from .default_component_factory import ViewerTreeForm


class ComponentsManager:
    def __init__(self) -> None:
        self.manager_widgets = {}
        self.setting = ViewerSetting()
        self.tree_form = ViewerTreeForm()

    def create_widget(self, widget_type: str):
        if widget_type == "tree_view":
            return self.tree_form.tree_view()
        elif widget_type == "camera_all_settings":
            return self.setting.camera_all_setting()
        else:
            raise ValueError(f"Unknown widget type: {widget_type}")

    def add_widgets(self, widget_list: list[dict[str, str]]):
        for widget in widget_list:
            widget_instance = self.create_widget(widget["type"])
            if widget_instance:  # Check if widget instance is not None
                self.manager_widgets[widget["type"]] = widget_instance
            else:
                print(f"Failed to create widget of type {widget['type']}")

    def setup_widgets(self, parent_widget):
        for widget_type, widget_instance in self.manager_widgets.items():
            if not isinstance(parent_widget, QWidget):
                raise TypeError("parent_widget must be a QtWidgets")
            if isinstance(widget_instance, QWidget):
                parent_widget.addWidget(widget_instance)
            else:
                raise TypeError(f"Widget instance of type {widget_type} is not a QWidget")
        return parent_widget
