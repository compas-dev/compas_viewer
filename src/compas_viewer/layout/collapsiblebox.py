from typing import Optional

from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QToolButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget


class CollapsibleBox(QWidget):

    def __init__(self, parent: Optional[QWidget] = None, expend: bool = False):
        super().__init__(parent=parent)
        self._parent = parent
        self._expanded = expend
        self.toggle_button = QToolButton(parent=self._parent)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.setIconSize(QSize(8, 8))
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        self.content_area = QScrollArea()
        self.content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

    def on_pressed(self):
        self._expanded = not self.toggle_button.isChecked()
        if self._expanded:
            self.expand()
        else:
            self.collapse()

    def get_content_height(self):
        return self._layout.sizeHint().height()

    def setContentLayout(self, layout):
        self._layout = layout
        self.content_area.setLayout(layout)
        self._collapsed_height = self.sizeHint().height()

    def expand(self):
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow)
        self.setFixedHeight(self._collapsed_height + self.get_content_height())
        self.content_area.setMaximumHeight(self.get_content_height())

    def collapse(self):
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.setFixedHeight(self._collapsed_height)
        self.content_area.setMaximumHeight(0)
