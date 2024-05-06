from PySide6 import QtGui
from PySide6 import QtWidgets


class BoxFactory:
    def __init__(self) -> None:
        self.spacing: int = 8

    def double_edit_widget(self, label_name: str, value: float, minval: float, maxval: float) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        validator = QtGui.QDoubleValidator()
        validator.setRange(minval, maxval)
        label = QtWidgets.QLabel()
        label.setText(label_name)
        line_edit = QtWidgets.QLineEdit()
        line_edit.setText(str(value))
        line_edit.setValidator(validator)
        layout.addWidget(label)
        layout.addWidget(line_edit)
        layout.setSpacing(self.spacing)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        return widget

    def double_spinner_widget(self, label_name: str, value: float, minval: float, maxval: float) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        spinner = QtWidgets.QSpinBox()
        label = QtWidgets.QLabel()
        label.setText(label_name)
        spinner.setMinimum(minval)
        spinner.setMaximum(maxval)
        spinner.setValue(value)
        layout.addWidget(label)
        layout.addWidget(spinner)
        layout.setSpacing(self.spacing)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        return widget
