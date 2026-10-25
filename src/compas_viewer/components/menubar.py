from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast

from PySide6.QtGui import QAction
from PySide6.QtGui import QActionGroup
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QMenuBar

from compas_viewer.components.component import Component
from compas_viewer.uidefinitions import UIItem

from .mainwindow import MainWindow


class MenuBar(Component):
    """Build the configured application menu bar.

    Parameters
    ----------
    window
        Main window that owns the menu bar.

    """

    def __init__(self, window: MainWindow) -> None:
        super().__init__()
        self.widget = window.widget.menuBar()
        self._menus: list[QMenu] = []
        self._groups: list[QActionGroup] = []
        self._actions: list[QAction] = []
        self._state_actions: dict[str, list[tuple[QAction, object]]] = {}
        self.viewer.state.changed.connect(self._on_state_changed)
        self.load_items()

    @property
    def items(self) -> list[UIItem]:
        """list[UIItem]: Runtime menu definitions."""
        return self.viewer.menu_items

    def load_items(
        self,
        items: list[UIItem] | None = None,
        parent: QMenuBar | QMenu | None = None,
    ) -> list[QAction]:
        """Create menu actions from configuration definitions.

        Parameters
        ----------
        items
            Menu definitions. The viewer configuration is used when omitted.
        parent
            Menu or menu bar that receives the actions.

        Returns
        -------
        list[QAction]
            Actions created directly for the supplied definitions.

        """
        items = items or self.items
        target = cast(QMenuBar | QMenu, parent or self.widget)

        actions: list[QAction] = []

        for item in items:
            text = item.get("title", None)
            itemtype = item.get("type", None)
            command_id = item.get("command", None)
            action = self.viewer.commands[command_id] if command_id else None
            args = item.get("args") or []
            kwargs = item.get("kwargs") or {}

            if itemtype == "separator":
                target.addSeparator()

            elif action:
                a = self.add_action(text=cast(str, text), action=action, parent=target, args=args, kwargs=kwargs)
                self._actions.append(a)
                actions.append(a)

                if itemtype == "checkbox":
                    a.setCheckable(True)

                state_path = item.get("state")
                if state_path:
                    expected = item.get("value", True)
                    a.setCheckable(True)
                    self._state_actions.setdefault(state_path, []).append((a, expected))
                    a.setChecked(self.viewer.state.get(state_path) == expected)
                elif itemtype == "checkbox":
                    state = item.get("checked", False)
                    a.setChecked(state if not callable(state) else state(self.viewer))

                if action.keybinding is not None:
                    a.setShortcut(action.keybinding)

            else:
                if items := item.get("items"):
                    if not itemtype or itemtype == "menu":
                        menu = target.addMenu(cast(str, text))
                        self._menus.append(menu)
                        self.load_items(items=items, parent=menu)

                    elif itemtype == "group":
                        group = QActionGroup(self.widget)
                        group.setExclusive(item.get("exclusive", True))
                        self._groups.append(group)
                        selected = item.get("selected", 0)
                        if callable(selected):
                            selected = selected(self.viewer)

                        menu = target.addMenu(cast(str, text))
                        self._menus.append(menu)
                        for i, a in enumerate(self.load_items(items=items, parent=menu)):
                            a.setCheckable(True)
                            if not any(a is registered for entries in self._state_actions.values() for registered, _ in entries) and i == selected:
                                a.setChecked(True)
                            group.addAction(a)

                    else:
                        raise NotImplementedError

                else:
                    menu = target.addMenu(cast(str, text))
                    self._menus.append(menu)
                    raise ValueError(f"Menu item {text!r} has neither a command nor child items.")

        return actions

    def reload(self) -> None:
        """Rebuild the menu bar from the current runtime definitions."""
        self.widget.clear()
        self._menus.clear()
        self._groups.clear()
        self._actions.clear()
        self._state_actions.clear()
        self.load_items()

    def _on_state_changed(self, path: str, value: object) -> None:
        """Synchronize actions bound to a changed viewer-state path."""
        for action, expected in self._state_actions.get(path, []):
            action.setChecked(value == expected)

    def add_action(
        self,
        *,
        text: str,
        action: Callable[..., object],
        parent: QMenuBar | QMenu,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
        icon: str | None = None,
    ) -> QAction:
        """Add a configured action to a menu.

        Parameters
        ----------
        text
            Visible action label.
        action
            Callback invoked by the action.
        parent
            Menu or menu bar receiving the action.
        args
            Positional callback arguments.
        kwargs
            Keyword callback arguments.
        icon
            Optional icon identifier; currently unsupported.

        Returns
        -------
        QAction
            The created action.

        """
        args = args or []
        kwargs = kwargs or {}
        if icon:
            raise NotImplementedError
        return parent.addAction(text, partial(action, *args, **kwargs))
