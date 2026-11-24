from collections.abc import Callable
from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from PySide6.QtCore import QEvent
from PySide6.QtCore import QObject
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtGui import QActionGroup
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QAbstractSpinBox
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QMenuBar
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QWidget

from compas_viewer.components.component import Component
from compas_viewer.uidefinitions import UIItem

from .mainwindow import MainWindow

if TYPE_CHECKING:
    from .sidebar import SideBarRight

_EDITOR_TYPES = (QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox, QComboBox)


class _GlobalEscapeFilter(QObject):
    """Route unmodified Escape through one window-level command path."""

    def __init__(self, callback: Callable[[], object], parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._callback = callback

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Handle Escape unless a focused editor owns the key event."""
        if event.type() != QEvent.Type.KeyPress or not isinstance(event, QKeyEvent):
            return False
        if event.key() != Qt.Key.Key_Escape or event.modifiers() != Qt.KeyboardModifier.NoModifier:
            return False
        if isinstance(QApplication.focusWidget(), _EDITOR_TYPES) or isinstance(watched, _EDITOR_TYPES):
            return False
        self._callback()
        event.accept()
        return True


class _GlobalDeleteFilter(QObject):
    """Route unmodified Delete within the owning window."""

    def __init__(self, callback: Callable[[], object], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._callback = callback

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Handle Delete unless a focused editor owns the key event."""
        if event.type() != QEvent.Type.KeyPress or not isinstance(event, QKeyEvent):
            return False
        if event.key() != Qt.Key.Key_Delete or event.modifiers() != Qt.KeyboardModifier.NoModifier:
            return False
        parent = self.parent()
        if isinstance(parent, QWidget) and (not isinstance(watched, QWidget) or watched.window() is not parent.window()):
            return False
        if isinstance(QApplication.focusWidget(), _EDITOR_TYPES) or isinstance(watched, _EDITOR_TYPES):
            return False
        self._callback()
        event.accept()
        return True


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
        self._command_actions: dict[str, list[QAction]] = {}
        self._state_actions: dict[str, list[tuple[QAction, object]]] = {}
        self._escape_filter = _GlobalEscapeFilter(self._deselect_or_cancel, self.widget)
        self._delete_filter = _GlobalDeleteFilter(self._delete_from_focus, self.widget)
        self.viewer.app.installEventFilter(self._escape_filter)
        self.viewer.app.installEventFilter(self._delete_filter)
        self.viewer.state.changed.connect(self._on_state_changed)
        self.load_items()

    def _deselect_or_cancel(self) -> object:
        """Cancel measurement or invoke Deselect All for global Escape."""
        if self.viewer.cancel_measurement():
            return None
        command = self.viewer.commands["viewer.deselect_all"]
        return command.callback(self.viewer)

    def _delete_from_focus(self) -> object:
        """Invoke contextual deletion for the focused interaction domain."""
        command = self.viewer.commands["viewer.delete_selected"]
        return command.callback(self.viewer, source="context")

    def bind_sidebar(self, sidebar: "SideBarRight") -> None:
        """Bind contextual menu enablement after sidebar construction."""
        self._sidebar = sidebar
        sidebar.widget.currentChanged.connect(self._update_delete_action)
        self._update_delete_action()

    def _update_delete_action(self, _index: int | None = None) -> None:
        """Enable menu deletion only for content domains that own deletion."""
        enabled = self._sidebar.current_tab in {"Scene", "Annotations"}
        for action in self._command_actions.get("viewer.delete_selected", ()):
            action.setEnabled(enabled)

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
                if command_id is not None:
                    self._command_actions.setdefault(command_id, []).append(a)

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

                if action.keybinding is not None and action.keybinding not in {"Escape", "Delete"}:
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
        self._command_actions.clear()
        self._state_actions.clear()
        self.load_items()
        if hasattr(self, "_sidebar"):
            self._update_delete_action()

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
