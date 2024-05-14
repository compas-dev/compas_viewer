from PySide6 import QtGui
from PySide6 import QtWidgets


class BaseWidgetFactory:
    def __init__(self) -> None:
        self.spacing: int = 8

    def setup_layout(self, layout: QtWidgets.QHBoxLayout):
        layout.setSpacing(self.spacing)
        layout.setContentsMargins(0, 0, 0, 0)


class DoubleEditWidget(BaseWidgetFactory):
    def __call__(self, label_name: str, value: float, minval: float, maxval: float) -> QtWidgets.QWidget:
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
        self.setup_layout(layout)
        widget.setLayout(layout)
        return widget


class DoubleSpinnerWidget(BaseWidgetFactory):
    def __call__(self, label_name: str, value: float, minval: float, maxval: float) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        spinner = QtWidgets.QSpinBox()
        label = QtWidgets.QLabel(label_name)
        spinner.setMinimum(minval)
        spinner.setMaximum(maxval)
        spinner.setValue(value)
        layout.addWidget(label)
        layout.addWidget(spinner)
        self.setup_layout(layout)
        widget.setLayout(layout)
        return widget


class LabelWidget(BaseWidgetFactory):
    def __call__(self, text: str) -> QtWidgets.QWidget:
        label = QtWidgets.QLabel()
        label.setText(text)
        return label
