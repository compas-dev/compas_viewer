from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from .component import Component


class Container(Component):
    """A container component that can hold other components in a vertical layout.

    The Container class provides a flexible way to organize and display multiple
    components in a vertical arrangement. It supports both scrollable and non-scrollable
    modes, making it suitable for various UI layouts.

    Parameters
    ----------
    scrollable : bool, optional
        If True, creates a scrollable container using QScrollArea.
        If False, creates a standard container with QWidget.
        Default is False.

    Attributes
    ----------
    scrollable : bool
        Whether the container is scrollable.
    widget : QWidget or QScrollArea
        The main widget that contains all child components.
    layout : QVBoxLayout
        The vertical layout that arranges child components.

    Examples
    --------
    >>> # Create a simple container
    >>> container = Container()
    >>> container.add(some_component)

    >>> # Create a scrollable container
    >>> scrollable_container = Container(scrollable=True)
    >>> scrollable_container.add(component1)
    >>> scrollable_container.add(component2)
    """

    def __init__(self, scrollable=False):
        self.scrollable = scrollable
        if self.scrollable:
            self.widget = QScrollArea()
            self.widget.setWidgetResizable(True)
            self._scroll_content = QWidget()
            self._scroll_layout = QVBoxLayout(self._scroll_content)
            self._scroll_layout.setAlignment(Qt.AlignTop)
            self.widget.setWidget(self._scroll_content)
            self.layout = QVBoxLayout()
            self.layout.setSpacing(0)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self._scroll_layout.addLayout(self.layout)
        else:
            self.widget = QWidget()
            self.layout = QVBoxLayout()
            self.layout.setSpacing(0)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.widget.setLayout(self.layout)

    def add(self, component: "Component") -> None:
        """Add a component to the container."""
        self.layout.addWidget(component.widget)
        self.children.append(component)

    def remove(self, component: "Component") -> None:
        """Remove a component from the container."""
        self.layout.removeWidget(component.widget)
        self.children.remove(component)

    def reset(self):
        """Reset the container to its initial state."""
        self.children = []
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

    def display_text(self, text: str) -> None:
        """Display a text when there is nothing else to show."""
        self.reset()
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: gray; font-style: italic; padding: 10px;")
        self.layout.addWidget(label)
