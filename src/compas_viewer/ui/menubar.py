from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Optional

from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QMenuBar
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from .mainwindow import MainWindow


class MenuBar:
    def __init__(self, parent: "MainWindow", items: list[dict]) -> None:
        self.parent = parent
        self.items = items
        self.widget: QMenuBar = self.parent.widget.menuBar()
        self.widget.clear()
        self.add_menu(items=self.items, parent=self.widget)

    def add_menu(self, *, items, parent: QMenu):
        if not items:
            return

        for item in items:
            text = item.get("title", None)
            itemtype = item.get("type", None)
            action = item.get("action", None)
            args = item.get("args") or []
            kwargs = item.get("kwargs") or {}

            if itemtype == "separator":
                parent.addSeparator()
            elif itemtype == "button":
                self.add_action(text=text, action=action, parent=parent, args=args, kwargs=kwargs)
            elif itemtype == "action":
                self.add_action(text=text, action=action, parent=parent, args=args, kwargs=kwargs)
            elif action:
                self.add_action(text=text, action=action, parent=parent, args=args, kwargs=kwargs)
            else:
                if items := item.get("items"):
                    if not itemtype or itemtype == "menu" or itemtype == "select":
                        menu = parent.addMenu(text)
                        self.add_menu(items=items, parent=menu)
                    elif itemtype == "radio":
                        raise NotImplementedError
                    else:
                        raise NotImplementedError
                else:
                    menu = parent.addMenu(text)
                    self.add_menu(items=[{"title": "PLACEHOLDER", "action": lambda: print("PLACEHOLDER")}], parent=menu)

    def add_action(
        self,
        *,
        text: str,
        action: Callable,
        parent: QWidget,
        args: Optional[list[Any]] = None,
        kwargs: Optional[dict] = None,
        icon: Optional[str] = None,
    ):
        args = args or []
        kwargs = kwargs or {}
        if icon:
            raise NotImplementedError
        return parent.addAction(text, partial(action, *args, **kwargs))
