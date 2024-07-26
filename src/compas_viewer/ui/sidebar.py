from typing import TYPE_CHECKING
from typing import Callable

from PySide6 import QtCore
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QTabWidget

from compas_viewer.components import Sceneform
from compas_viewer.components.objectsetting import ObjectSetting

if TYPE_CHECKING:
    from .ui import UI

# Factory registry
type_registry = {
    "Sceneform": Sceneform,
    "ObjectSetting": ObjectSetting,
}


class SideBarRight:
    def __init__(self, ui: "UI", show: bool, items: list[dict[str, Callable]]) -> None:
        self.ui = ui
        self.widget = QSplitter(QtCore.Qt.Orientation.Vertical)
        self.widget.setChildrenCollapsible(True)
        self._tab_widget = None
        self.show = show
        self.hide_widget = True
        self.items = items

        # # Tab 1 setup
        # self.tab1_content = QWidget()
        # self.tab1_scroll_area = QScrollArea(self.tab1_content)
        # self.tab1_scroll_area.setWidgetResizable(True)
        # self.tab1_scroll_content = QWidget()
        # self.tab1_scroll_layout = QVBoxLayout(self.tab1_scroll_content)
        # self.tab1_scroll_layout.setAlignment(Qt.AlignTop)
        # self.tab1_scroll_area.setWidget(self.tab1_scroll_content)

        # tab1_layout = QVBoxLayout(self.tab1_content)
        # tab1_layout.addWidget(self.tab1_scroll_area)
        # self.tab_widget.addTab(self.tab1_content, "Tab 1")

    @property
    def tab_widget(self):
        if self._tab_widget is None:
            self._tab_widget = QTabWidget(self.widget)

        return self._tab_widget

    @property
    def show(self):
        return self.widget.isVisible()

    @show.setter
    def show(self, value: bool):
        self.widget.setVisible(value)

    @property
    def show_sceneform(self):
        return self.Sceneform.isVisible()

    @show_sceneform.setter
    def show_sceneform(self, value: bool):
        self.Sceneform.setVisible(value)

    @property
    def show_objectsetting(self):
        return self.ObjectSetting.isVisible()

    @show_objectsetting.setter
    def show_objectsetting(self, value: bool):
        self.ObjectSetting.setVisible(value)

    def add_items(self) -> None:
        if not self.items:
            return

        for item in self.items:
            # area = item.get("area", None)
            itemtype = item.get("type", None)
            items = item.get("items", None)

            if itemtype in type_registry:
                if items is None:
                    raise ValueError("Please setup config for Sceneform")
                widget = type_registry[itemtype](items=items)
                # set the attribute dynamically
                setattr(self, itemtype, widget)
                self.widget.addWidget(widget)

    def update(self):
        self.widget.update()
        for widget in self.widget.children():
            widget.update()
