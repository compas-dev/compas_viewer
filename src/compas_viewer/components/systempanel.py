"""Viewer-wide camera, display, and measurement settings."""

from typing import Literal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGroupBox
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from .component import Component

SystemSection = Literal["Camera", "Display", "Units and Measurement"]


class SystemPanel(Component):
    """Display Viewer-wide settings in one scrollable page."""

    def __init__(self) -> None:
        super().__init__()
        self.widget = QScrollArea()
        self.widget.setWidgetResizable(True)
        self.widget.setFrameShape(QFrame.Shape.NoFrame)
        self.content = QWidget()
        self.layout = QVBoxLayout(self.content)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setWidget(self.content)
        self.sections: dict[SystemSection, tuple[QGroupBox, Component]] = {}

    def add_section(self, name: SystemSection, component: Component) -> None:
        """Add one labeled system-settings section.

        Parameters
        ----------
        name
            Closed section identifier.
        component
            Settings component displayed in the section.

        """
        if name in self.sections:
            raise ValueError(f"System section {name!r} already exists.")
        group = QGroupBox(name)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.addWidget(component.widget)
        self._fit_component(component)
        self.layout.addWidget(group)
        self.sections[name] = (group, component)

    def focus_section(self, name: SystemSection) -> None:
        """Scroll one system-settings section into view.

        Parameters
        ----------
        name
            Section to reveal.

        Raises
        ------
        ValueError
            If the configured sidebar does not contain `name`.

        """
        try:
            group, _component = self.sections[name]
        except KeyError:
            raise ValueError(f"System section {name!r} is not configured.") from None
        self.widget.ensureWidgetVisible(group)
        group.setFocus(Qt.FocusReason.OtherFocusReason)

    def update(self) -> None:
        """Update every configured system-settings section."""
        for _group, component in self.sections.values():
            component.update()
            self._fit_component(component)
        self.widget.update()

    @staticmethod
    def _fit_component(component: Component) -> None:
        """Let the outer page own scrolling for nested setting containers."""
        widget = component.widget
        if not isinstance(widget, QScrollArea):
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            return
        widget.setFrameShape(QFrame.Shape.NoFrame)
        widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        contents = widget.widget()
        if contents is not None:
            contents.adjustSize()
            widget.setFixedHeight(contents.sizeHint().height())
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


__all__ = ["SystemPanel", "SystemSection"]
