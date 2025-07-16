from functools import partial
from typing import Any
from typing import Callable
from typing import Optional

from PySide6.QtGui import QAction
from PySide6.QtGui import QActionGroup
from PySide6.QtWidgets import QWidget

from compas_viewer.commands import Command
from compas_viewer.components.component import Component

from .mainwindow import MainWindow


class MenuBar(Component):
    def __init__(self, window: MainWindow) -> None:
        super().__init__()
        self.widget = window.widget.menuBar()
        self.load_items()

    @property
    def items(self):
        return self.viewer.config.ui.menubar.items

    def load_items(self, items=None, parent=None) -> list[QAction]:
        items = items or self.items
        parent = parent or self.widget

        actions = []

        for item in items:
            text = item.get("title", None)
            itemtype = item.get("type", None)
            action = item.get("action", None)
            args = item.get("args") or []
            kwargs = item.get("kwargs") or {}

            if itemtype == "separator":
                parent.addSeparator()

            elif action:
                a = self.add_action(text=text, action=action, parent=parent, args=args, kwargs=kwargs)
                actions.append(a)

                if itemtype == "checkbox":
                    state = item.get("checked", False)
                    a.setCheckable(True)
                    a.setChecked(state if not callable(state) else state(self.viewer))

                if isinstance(action, Command):
                    if action.keybinding is not None:
                        a.setShortcut(action.keybinding)

            else:
                if items := item.get("items"):
                    if not itemtype or itemtype == "menu":
                        menu = parent.addMenu(text)
                        self.load_items(items=items, parent=menu)

                    elif itemtype == "group":
                        group = QActionGroup(self.widget)
                        group.setExclusive(item.get("exclusive", True))

                        menu = parent.addMenu(text)
                        for i, a in enumerate(self.load_items(items=items, parent=menu)):
                            a.setCheckable(True)
                            if i == item.get("selected", 0):
                                a.setChecked(True)
                            group.addAction(a)

                    else:
                        raise NotImplementedError

                else:
                    menu = parent.addMenu(text)
                    self.load_items(items=[{"title": "PLACEHOLDER", "action": lambda: print("PLACEHOLDER")}], parent=menu)

        return actions

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
