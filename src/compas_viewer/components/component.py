from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QScrollArea
from PySide6.QtCore import Qt
from compas_viewer.base import Base


class Component(Base):
    def __init__(self, scrollable=False):
        super().__init__()
        self.scrollable = scrollable

        # Create widgets once in init
        if self.scrollable:
            self.widget = QScrollArea()
            self.widget.setWidgetResizable(True)
            self.scroll_content = QWidget()
            self.scroll_layout = QVBoxLayout(self.scroll_content)
            self.scroll_layout.setAlignment(Qt.AlignTop)
            self.widget.setWidget(self.scroll_content)
            self.layout = QVBoxLayout()
            self.layout.setSpacing(0)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.scroll_layout.addLayout(self.layout)
        else:
            self.widget = QWidget()
            self.layout = QVBoxLayout()
            self.layout.setSpacing(0)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.widget.setLayout(self.layout)

    def update(self):
        self.widget.update()

    def add(self, component: "Component") -> None:
        self.layout.addWidget(component.widget)
        self.children.append(component)

    def remove(self, component: "Component") -> None:
        self.layout.removeWidget(component.widget)
        self.children.remove(component)

    def reset(self):
        # Clear existing children
        self.children = []

        # Clear the layout without recreating widgets
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
