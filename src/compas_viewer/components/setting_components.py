from PySide6 import QtWidgets

from .widget_tools import DoubleEditWidget


class SettingComponents:
    def __init__(self) -> None:
        self.widgets = {}

    def lazy_init(self):
        # Dynamically call methods based on naming convention
        for name in dir(self):
            if name.endswith("_setting") and callable(getattr(self, name)):
                method = getattr(self, name)
                method()

    def register_widget(self, name: str, widget: QtWidgets.QGroupBox) -> None:
        self.widgets[name] = widget

    def get_widget(self, name: str) -> QtWidgets.QGroupBox:
        return self.widgets.get(name)

    def create_setting_group(self, title: str, settings: list[tuple[str, float, float, float]]) -> None:
        double_edit_widgets = DoubleEditWidget()
        widget = QtWidgets.QGroupBox(title)
        layout = QtWidgets.QVBoxLayout()
        for setting in settings:
            layout.addWidget(double_edit_widgets(*setting))
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)
        widget.setLayout(layout)
        self.register_widget(title, widget)

    def camera_target_setting(self):
        return self.create_setting_group("Camera_Target", [("X", 0, 0, 100000), ("Y", 0, 0, 100000), ("Z", 0, 0, 100000)])

    def camera_location_setting(self):
        return self.create_setting_group("Camera_Location", [("X", 0, 0, 100000), ("Y", 0, 0, 100000), ("Z", 0, 0, 100000)])

    def camera_pov_setting(self):
        return self.create_setting_group("Camera_POV", [("FOV", 50, 10, 80), ("NEAR", 0.1, 0.001, 1000), ("FAR", 1000, 1, 10000000)])
