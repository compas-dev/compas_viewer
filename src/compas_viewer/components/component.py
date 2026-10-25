from PySide6.QtWidgets import QWidget

from compas_viewer.base import Base


class Component(Base):
    """Provide the common widget and visibility interface for UI components."""

    def __init__(self) -> None:
        super().__init__()
        self.widget = QWidget()
        self._show = True

    def update(self) -> None:
        """Request a repaint of the component widget."""
        self.widget.update()

    @property
    def show(self) -> bool:
        """bool: Whether the component widget is visible."""
        return self._show

    @show.setter
    def show(self, value: bool) -> None:
        self._show = value
        self.widget.setVisible(value)
