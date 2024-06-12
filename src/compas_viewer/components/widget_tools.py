from PySide6 import QtWidgets


class BaseWidgetFactory:
    def __init__(self) -> None:
        self.spacing: int = 8

    def setup_layout(self, layout: QtWidgets.QHBoxLayout):
        layout.setSpacing(self.spacing)
        layout.setContentsMargins(0, 0, 0, 0)


class LabelWidget(BaseWidgetFactory):
    def __call__(self, text: str) -> QtWidgets.QWidget:
        label = QtWidgets.QLabel()
        label.setText(text)
        return label
