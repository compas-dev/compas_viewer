from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QSizePolicy
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

        self.text_edit = QTextEdit()
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit.setMaximumSize(85, 25)
        self.text_edit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.text_edit.setText(text)

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)
