from typing import Optional

from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QToolButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget


class CollapsibleBox(QWidget):
    """Collapsible box widget.

    Parameters
    ----------
    name : str, optional
        Name of the collapsible box.
    expend : bool, optional
        Whether the box is expanded or not.

    See Also
    --------
    :class:`compas_viewer.layout.Slider`

    References
    ----------
    :PySide6:`PySide6/QWidgets/QWidget`
    """

    def __init__(self, name: Optional[str] = None, expend: bool = True):
        super().__init__()
        self.name = name
        self._expanded = expend

        self.toggle_button = QToolButton()
        self.toggle_button.setText(self.name or "")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.setIconSize(QSize(8, 8))
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        self.content_area = QScrollArea()
        self.content_area.setLayout(QVBoxLayout())
        _layout = QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.addWidget(self.toggle_button)
        _layout.addWidget(self.content_area)

        if self._expanded:
            self.expand()

    def on_pressed(self):
        """Toggle the box."""
        self._expanded = not self._expanded
        if self._expanded:
            self.expand()
        else:
            self.collapse()

    def expand(self):
        """Expand the box."""
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow)
        self.content_area.show()
        self.content_area.setMinimumHeight(self.content_area.layout().sizeHint().height())

    def collapse(self):
        """Collapse the box."""
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.content_area.hide()

    def update(self):
        """Update the layout."""

        if self._expanded:
            self.expand()
        else:
            self.collapse()

        super().update()
