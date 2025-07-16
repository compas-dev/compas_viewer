from PySide6.QtWidgets import QWidget

from compas_viewer.base import Base


class Component(Base):
    """A base class for all UI components in the viewer.

    Attributes
    ----------
    widget : QWidget
        The main widget that contains all child components.

    """

    def __init__(self):
        super().__init__()
        self.widget = QWidget()
        self._show = True

    def update(self):
        self.widget.update()

    @property
    def show(self):
        return self._show

    @show.setter
    def show(self, value: bool):
        self._show = value
        self.widget.setVisible(value)
