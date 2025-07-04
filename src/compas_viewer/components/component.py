from PySide6.QtWidgets import QWidget

from compas_viewer.base import Base


class Component(Base):
    def __init__(self):
        self.widget = QWidget()

    def update(self):
        self.widget.update()
