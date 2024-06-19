from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QWidget


class TextEdit(QWidget):
    """
    A customizable QTextEdit widget for Qt applications, supporting text alignment and font size adjustments.
    """

    def __init__(
        self,
        text: str = None,
    ):
        super().__init__()

        self._default_layout = None
        self.layout = self.default_layout
        self.layout.setAlignment(Qt.AlignRight)
        self.text_edit = QTextEdit()
        self.text_edit.setMaximumSize(100, 25)
        self.text_edit.setText(text)
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)

    @property
    def default_layout(self):
        if self._default_layout is None:
            from compas_viewer.components.layout import DefaultLayout

            self._default_layout = DefaultLayout(QHBoxLayout()).get_layout()
        return self._default_layout
