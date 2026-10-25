from typing import Literal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from .component import Component


class Container(Component):
    """A container component that can hold other components in a vertical layout.

    The Container class provides a flexible way to organize and display multiple
    components in a vertical arrangement. It supports scrollable, splitter, and standard
    container modes, making it suitable for various UI layouts.

    Parameters
    ----------
    container_type
        Type of container to create. Options are:
        - None or "standard": Creates a standard container with QWidget
        - "scrollable": Creates a scrollable container using QScrollArea
        - "splitter": Creates a resizable splitter container using QSplitter
        Default is None.
    compact
        Whether child components should use the shared compact control-row
        spacing and height.

    Examples
    --------
    >>> # Create a simple container
    >>> container = Container()
    >>> container.add(some_component)

    >>> # Create a scrollable container
    >>> scrollable_container = Container(container_type="scrollable")
    >>> scrollable_container.add(component1)
    >>> scrollable_container.add(component2)

    >>> # Create a splitter container
    >>> splitter_container = Container(container_type="splitter")
    >>> splitter_container.add(component1)
    >>> splitter_container.add(component2)

    """

    COMPACT_CONTENT_MARGINS = (6, 6, 6, 6)
    COMPACT_LAYOUT_SPACING = 2
    COMPACT_ROW_MARGINS = (6, 2, 6, 2)
    COMPACT_ROW_SPACING = 8
    COMPACT_ROW_MAXIMUM_HEIGHT = 34

    def __init__(self, container_type: Literal["standard", "scrollable", "splitter"] | None = None, *, compact: bool = False) -> None:
        self.container_type = container_type
        self.compact = compact
        self.children: list[Component] = []
        if self.container_type == "scrollable":
            self.widget = QScrollArea()
            self.widget.setWidgetResizable(True)
            self.widget.setContentsMargins(0, 0, 0, 0)
            self._scroll_content = QWidget()
            self._scroll_content.setContentsMargins(0, 0, 0, 0)
            self._scroll_layout = QVBoxLayout(self._scroll_content)
            self._scroll_layout.setAlignment(Qt.AlignTop)
            self._scroll_layout.setContentsMargins(0, 0, 0, 0)
            self.widget.setWidget(self._scroll_content)
            self.layout = QVBoxLayout()
            self.layout.setSpacing(0)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self._scroll_layout.addLayout(self.layout)
        elif self.container_type == "splitter":
            self.widget = QSplitter(Qt.Orientation.Vertical)
            self.widget.setChildrenCollapsible(True)
            self.widget.setContentsMargins(0, 0, 0, 0)
            self.layout = None  # Splitter doesn't use layout
        else:
            self.widget = QWidget()
            self.widget.setContentsMargins(0, 0, 0, 0)
            self.layout = QVBoxLayout()
            self.layout.setSpacing(0)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.widget.setLayout(self.layout)

        if self.compact and self.layout is not None:
            self.layout.setContentsMargins(*self.COMPACT_CONTENT_MARGINS)
            self.layout.setSpacing(self.COMPACT_LAYOUT_SPACING)

    def add(self, component: "Component") -> None:
        """Add a component to the container.

        Parameters
        ----------
        component
            Component to append.

        """
        if component in self.children:
            return

        if self.container_type == "splitter":
            self.widget.addWidget(component.widget)
            child_count = self.widget.count()
            height = self.widget.height()
            if child_count > 0:
                equal_sizes = [height // child_count] * child_count
                self.widget.setSizes(equal_sizes)
        else:
            assert self.layout is not None
            if self.compact:
                self._compact_component(component)
            self.layout.addWidget(component.widget)
        self.children.append(component)

    def _compact_component(self, component: Component) -> None:
        """Apply the shared compact sidebar style to a child component.

        Parameters
        ----------
        component
            Component whose widget and internal layout should be compacted.

        """
        layout = component.widget.layout()
        if layout is not None:
            layout.setContentsMargins(*self.COMPACT_ROW_MARGINS)
            layout.setSpacing(self.COMPACT_ROW_SPACING)
        component.widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        component.widget.setMaximumHeight(self.COMPACT_ROW_MAXIMUM_HEIGHT)

    def remove(self, component: "Component") -> None:
        """Remove a component from the container.

        Parameters
        ----------
        component
            Component to remove.

        """
        if self.container_type == "splitter":
            component.widget.setParent(None)
        else:
            assert self.layout is not None
            self.layout.removeWidget(component.widget)
        self.children.remove(component)

    def update(self) -> None:
        """Update the container and its children."""
        self.widget.update()
        for child in self.children:
            child.update()

    def reset(self) -> None:
        """Reset the container to its initial state."""
        self.children = []
        if self.container_type == "splitter":
            # For splitter, remove all widgets
            while self.widget.count():
                child = self.widget.widget(0)
                if child:
                    child.setParent(None)
        else:
            # For layout-based containers
            assert self.layout is not None
            while self.layout.count():
                child = self.layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)

    def display_text(self, text: str) -> None:
        """Replace the container contents with a text label.

        Parameters
        ----------
        text
            Text to display.

        """
        self.reset()
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: gray; font-style: italic; padding: 10px;")
        if self.container_type == "splitter":
            self.widget.addWidget(label)
        else:
            assert self.layout is not None
            self.layout.addWidget(label)
