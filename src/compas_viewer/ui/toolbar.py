from functools import partial
from typing import Any
from typing import Callable
from typing import Optional

from PySide6.QtWidgets import QComboBox

from compas_viewer.base import Base
from compas_viewer.components import Button


class ToolBar(Base):
    def __init__(self) -> None:
        self.widget = None

    def lazy_init(self):
        self.widget = self.viewer.ui.window.addToolBar("Tools")
        self.widget.setMovable(False)
        self.widget.setObjectName("Tools")
        self.widget.setHidden(not self.viewer.config.ui.toolbar.show)

        items = self.viewer.config.ui.toolbar.items
        if not items:
            return

        for item in items:
            text = item.get("title", None)
            tooltip = item.get("tooltip", None)
            itemtype = item.get("type", None)
            action = item.get("action", None)
            icon = item.get("icon", None)

            if itemtype == "separator":
                raise NotImplementedError
            elif itemtype == "button":
                self.add_action(tooltip=tooltip, icon=icon, action=action)
            elif itemtype == "action":
                self.add_action(text=text, action=action)
            elif itemtype == "select":
                self.add_combobox(item["items"], item["action"])
            elif action:
                self.add_action(text=text, action=action)

    def add_action(
        self,
        *,
        tooltip: str,
        text: Optional[str] = None,
        action: Callable,
        args: Optional[list[Any]] = None,
        kwargs: Optional[dict] = None,
        icon: Optional[str] = None,
    ):
        args = args or []
        kwargs = kwargs or {}
        return self.widget.addWidget(Button(text=text, tooltip=tooltip, icon_path=icon, action=partial(action, *args, **kwargs)))

    def add_combobox(self, items, action, title=None):
        combobox = QComboBox()
        for item in items:
            combobox.addItem(item["title"], item.get("value", item["title"]))
        combobox.currentIndexChanged.connect(lambda index: action(combobox.itemData(index)))
        self.widget.addWidget(combobox)
