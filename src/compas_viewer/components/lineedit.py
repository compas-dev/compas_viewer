from typing import Callable
from typing import Optional

from PySide6.QtCore import Qt

# from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QWidget


class LineEdit(QWidget):
    """
    A customizable QTextEdit widget for Qt applications, supporting text alignment and font size adjustments.
    """

    def __init__(
        self,
        text: Optional[str] = None,
        label: Optional[str] = None,
        action: Optional[Callable] = None,
    ):
        super().__init__()

        self.action = action

        label = QLabel(label)
        label.setStyleSheet("""margin-right: 8px;""")

        self.text_edit = QLineEdit()
        self.text_edit.setMaximumSize(85, 25)
        self.text_edit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.text_edit.setText(text)
        self.text_edit.setStyleSheet("""padding: 2px;""")

        # validator = QDoubleValidator()

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(label)
        self.layout.addWidget(self.text_edit)
        self.setLayout(self.layout)

        self.text_edit.returnPressed.connect(self.text_update)

    def text_update(self):
        try:
            value = float(self.text_edit.text())
        except ValueError:
            pass
        else:
            if self.action:
                self.action(self, value)
