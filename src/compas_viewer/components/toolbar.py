from functools import partial
from typing import Any
from typing import Callable
from typing import Optional

from compas_viewer.components import Button
from compas_viewer.components.component import Component

from .mainwindow import MainWindow


class ToolBar(Component):
    def __init__(self, window: MainWindow) -> None:
        super().__init__()
        self.widget = window.widget.addToolBar("Tools")
        self.widget.clear()
        self.widget.setMovable(False)
        self.widget.setObjectName("Tools")
        self.load_items()

    @property
    def items(self):
        return self.viewer.config.ui.toolbar.items

    def load_items(self):
        for item in self.items:
            text = item.get("title", None)
            tooltip = item.get("tooltip", None)
            itemtype = item.get("type", None)
            action = item.get("action", None)
            icon = item.get("icon", None)
            args = item.get("args") or []
            kwargs = item.get("kwargs") or {}

            if itemtype == "separator":
                raise NotImplementedError
            elif itemtype == "button":
                self.add_action(tooltip=tooltip, icon=icon, action=action, args=args, kwargs=kwargs)
            elif itemtype == "action":
                self.add_action(text=text, action=action, args=args, kwargs=kwargs)
            # elif itemtype == "select":
            #     self.add_combobox(item["items"], item["action"])
            elif action:
                self.add_action(text=text, action=action, args=args, kwargs=kwargs)

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

    # def add_combobox(self, items, action, title=None):
    #     combobox = QComboBox()
    #     for item in items:
    #         combobox.addItem(item["title"], item.get("value", item["title"]))
    #     combobox.currentIndexChanged.connect(lambda index: action(combobox.itemData(index)))
    #     self.widget.addWidget(combobox)
