from PySide6 import QtWidgets


class DoubleEdit(QtWidgets.QWidget):
    def __init__(self, name: str, default: float, min_val: float, max_val: float):
        super().__init__()
        self.layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(name)
        self.spinbox = QtWidgets.QDoubleSpinBox()
        self.spinbox.setValue(default)
        self.spinbox.setMinimum(min_val)
        self.spinbox.setMaximum(max_val)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spinbox)
        self.setLayout(self.layout)


class DoubleEditGroup(QtWidgets.QWidget):
    def __init__(self, title: str, settings: list[tuple[str, float, float, float]]):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)

        self.group_box = QtWidgets.QGroupBox(title)
        group_layout = QtWidgets.QVBoxLayout()

        for setting in settings:
            widget = DoubleEdit(*setting)
            group_layout.addWidget(widget)

        group_layout.setSpacing(4)
        group_layout.setContentsMargins(4, 4, 4, 4)
        self.group_box.setLayout(group_layout)

        self.layout.addWidget(self.group_box)
        self.setLayout(self.layout)
