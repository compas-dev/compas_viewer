from typing import TYPE_CHECKING
from typing import Callable
from typing import Optional

from PySide6 import QtCore
from PySide6.QtWidgets import QHeaderView
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QWidget

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
        self._tab_widget: Optional[QTabWidget] = None
        self.show = show
        self.hide_widget = True
        self.items = items

    @property
    def tab_widget(self):
        if self._tab_widget is None:
            self._tab_widget = QTabWidget(self.widget)
            self.widget.addWidget(self._tab_widget)
        return self._tab_widget

    @property
    def show(self):
        return self.widget.isVisible()

    @show.setter
    def show(self, value: bool):
        self.widget.setVisible(value)

    @property
    def show_sceneform(self):
        return getattr(self, "Sceneform", QWidget()).isVisible()

    @show_sceneform.setter
    def show_sceneform(self, value: bool):
        getattr(self, "Sceneform", QWidget()).setVisible(value)

    @property
    def show_objectsetting(self):
        return getattr(self, "ObjectSetting", QWidget()).isVisible()

    @show_objectsetting.setter
    def show_objectsetting(self, value: bool):
        getattr(self, "ObjectSetting", QWidget()).setVisible(value)

    def add_items(self) -> None:
        if not self.items:
            return

        for item in self.items:
            area = item.get("area", None)
            itemtype = item.get("type", None)
            items = item.get("items", None)

            if itemtype in type_registry:
                if items is None:
                    raise ValueError("Please setup config for Sceneform")
                widget = type_registry[itemtype](items=items)
                # set the attribute dynamically
                setattr(self, itemtype, widget)
                if area == "tab":
                    self.tab_widget.addTab(widget, itemtype)
                else:
                    self.widget.addWidget(widget)

    def update(self):
        self._update_recursive(self.widget)

    def _update_recursive(self, widget: QWidget) -> None:
        if not isinstance(widget, QHeaderView) and hasattr(widget, "update"):
            widget.update()
        for child in widget.findChildren(QWidget):
            self._update_recursive(child)
