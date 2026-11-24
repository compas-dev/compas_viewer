from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast

from PySide6.QtCore import QEvent
from PySide6.QtCore import QObject
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtGui import QGuiApplication
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QAbstractButton
from PySide6.QtWidgets import QButtonGroup
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QWidget

from compas_viewer.components import Button
from compas_viewer.components.component import Component
from compas_viewer.uidefinitions import UIItem

from .mainwindow import MainWindow


class _ToolbarSelector(QComboBox):
    """Report popup teardown after Qt has hidden its transient window."""

    popup_hidden = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._popup_cycle_active = False
        self._popup_hidden_scheduled = False
        self._popup_targets: list[QObject] = []

    @property
    def popup_cycle_active(self) -> bool:
        """bool: Whether one shown popup is awaiting teardown completion."""
        return self._popup_cycle_active

    def showPopup(self) -> None:  # noqa: N802
        """Start one popup cycle and observe the actual transient widgets."""
        self._popup_cycle_active = True
        self._popup_hidden_scheduled = False
        super().showPopup()
        self._observe_popup_targets()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Schedule one completion after the popup view or window hides."""
        if self._popup_cycle_active and event.type() == QEvent.Type.Hide and watched in self._popup_targets:
            self._schedule_popup_hidden()
        return super().eventFilter(watched, event)

    def _observe_popup_targets(self) -> None:
        """Install this selector on the current popup view and window."""
        for target in self._popup_targets:
            target.removeEventFilter(self)
        view = self.view()
        targets = (view, view.window())
        self._popup_targets = []
        for target in targets:
            if target not in self._popup_targets:
                target.installEventFilter(self)
                self._popup_targets.append(target)

    def _schedule_popup_hidden(self) -> None:
        """Defer one popup completion until Qt finishes transient teardown."""
        if self._popup_hidden_scheduled:
            return
        self._popup_hidden_scheduled = True
        QTimer.singleShot(0, self._finish_popup_cycle)

    def _finish_popup_cycle(self) -> None:
        """End the current popup cycle and request one focus restoration."""
        if not self._popup_hidden_scheduled:
            return
        self._popup_cycle_active = False
        self._popup_hidden_scheduled = False
        self.popup_hidden.emit()


class _ViewportFocusRestorer(QObject):
    """Restore renderer focus after Qt has returned focus to the main window."""

    def __init__(self, window: QWidget, restore: Callable[[], None]) -> None:
        super().__init__(window)
        self._window = window
        self._restore = restore
        self._pending = False
        self._selector: _ToolbarSelector | None = None
        app = cast(QGuiApplication, QGuiApplication.instance())
        app.focusWindowChanged.connect(self._on_focus_window_changed)

    def request(self, selector: _ToolbarSelector | None = None) -> None:
        """Request focus restoration when the owning window is ready."""
        self._pending = True
        self._selector = selector
        handle = self._window.windowHandle()
        if handle is not None:
            handle.requestActivate()
        self._window.activateWindow()
        QTimer.singleShot(0, self._restore_if_ready)

    def _on_focus_window_changed(self, _window: QWindow | None) -> None:
        """Recheck a pending request after the application focus window changes."""
        self._restore_if_ready()

    def _restore_if_ready(self) -> None:
        """Restore focus only after popup teardown and window activation finish."""
        if not self._pending:
            return
        handle = self._window.windowHandle()
        if handle is None or QGuiApplication.focusWindow() is not handle:
            return
        if not self._window.isActiveWindow():
            return
        if self._selector is not None and self._selector.popup_cycle_active:
            return
        self._pending = False
        self._selector = None
        self._restore()


class ToolBar(Component):
    """Build the configured toolbar for a main window.

    Parameters
    ----------
    window
        Main window that owns the toolbar.

    """

    def __init__(self, window: MainWindow) -> None:
        super().__init__()
        self.window = window
        self.widget = window.widget.addToolBar("Tools")
        self.widget.clear()
        self.widget.setMovable(False)
        self.widget.setObjectName("Tools")
        self._state_selectors: dict[str, list[tuple[QComboBox, tuple[object, ...]]]] = {}
        self._state_buttons: dict[str, list[tuple[QAbstractButton, object]]] = {}
        self._state_button_groups: dict[str, QButtonGroup] = {}
        self._focus_restorer = _ViewportFocusRestorer(
            window.widget,
            self._set_renderer_focus,
        )
        self.viewer.state.changed.connect(self._on_state_changed)
        self.load_items()

    @property
    def items(self) -> list[UIItem]:
        """list[UIItem]: Runtime toolbar definitions."""
        return self.viewer.toolbar_items

    def load_items(self) -> None:
        """Populate the toolbar from the viewer configuration."""
        for item in self.items:
            text = item.get("title", None)
            tooltip = item.get("tooltip", None)
            itemtype = item.get("type", None)
            command_id = item.get("command", None)
            action = self.viewer.commands[command_id] if command_id else None
            icon = item.get("icon", None)
            args = item.get("args") or []
            kwargs = item.get("kwargs") or {}

            if itemtype == "separator":
                raise NotImplementedError
            elif itemtype == "button":
                if item.get("state") is not None:
                    self._add_state_button(item)
                else:
                    restore_focus = command_id in {"viewer.zoom_selected", "viewer.zoom_extents", "viewer.capture_view"}
                    self.add_action(
                        tooltip=tooltip or text,
                        text=None if item.get("icon_only") else text,
                        accessible_name=text,
                        icon=icon,
                        action=partial(self._invoke_action, cast(Callable[..., object], action), restore_focus),
                        args=args,
                        kwargs=kwargs,
                    )
            elif itemtype == "action":
                self.add_action(text=text, action=cast(Callable[..., object], action), args=args, kwargs=kwargs)
            elif itemtype == "menu_button":
                self._add_menu_button(item)
            elif itemtype == "select":
                self._add_select(item)
            elif action:
                self.add_action(text=text, action=action, args=args, kwargs=kwargs)

    def add_action(
        self,
        *,
        tooltip: str | None = None,
        text: str | None = None,
        action: Callable[..., object],
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
        icon: str | None = None,
        accessible_name: str | None = None,
    ) -> QAction:
        """Add a configured action widget to the toolbar.

        Parameters
        ----------
        tooltip
            Optional hover text.
        text
            Optional button label.
        action
            Callback invoked by the button.
        args
            Positional callback arguments.
        kwargs
            Keyword callback arguments.
        icon
            Optional icon filename.
        accessible_name
            Optional semantic name for icon-only buttons.

        Returns
        -------
        QAction
            Toolbar action representing the button widget.

        """
        args = args or []
        kwargs = kwargs or {}
        button = Button(text=text, tooltip=tooltip, icon_path=icon, action=partial(action, *args, **kwargs))
        if accessible_name:
            button.widget.setAccessibleName(accessible_name)
        return self.widget.addWidget(button.widget)

    def _invoke_action(self, action: Callable[..., object], restore_focus: bool, *args: Any, **kwargs: Any) -> None:
        """Invoke one toolbar action and optionally restore viewport focus."""
        action(*args, **kwargs)
        if restore_focus:
            self._focus_restorer.request()

    def _add_menu_button(self, item: UIItem) -> None:
        """Add one narrow command menu button to the toolbar."""
        title = item.get("title")
        options = item.get("items")
        if not isinstance(title, str) or not title:
            raise ValueError("Toolbar menu buttons require a non-empty title.")
        if not isinstance(options, list) or not options:
            raise ValueError(f"Toolbar menu button {title!r} requires at least one option.")
        component = Button(
            text=None if item.get("icon_only") else title,
            tooltip=item.get("tooltip") or title,
            icon_path=item.get("icon"),
        )
        button = component.widget
        button.setObjectName(f"toolbar_menu_{title.lower().replace(' ', '_')}")
        button.setAccessibleName(title)
        menu = QMenu(button)
        menu.setObjectName(f"toolbar_menu_{title.lower().replace(' ', '_')}_items")
        for option in options:
            option_title = option.get("title")
            command_id = option.get("command")
            if not isinstance(option_title, str) or not option_title:
                raise ValueError(f"Toolbar menu button {title!r} contains an option without a title.")
            if not isinstance(command_id, str) or not command_id:
                raise ValueError(f"Toolbar menu option {option_title!r} requires a command.")
            command = self.viewer.commands[command_id]
            action = menu.addAction(option_title)
            action.setObjectName(f"toolbar_menu_{title.lower().replace(' ', '_')}_{option_title.lower().replace(' ', '_')}")
            action.triggered.connect(
                partial(
                    self._invoke_action,
                    command,
                    False,
                    *(option.get("args") or []),
                    **(option.get("kwargs") or {}),
                )
            )
        menu.aboutToHide.connect(self._focus_restorer.request)
        button.setMenu(menu)
        self.widget.addWidget(button)

    def _add_state_button(self, item: UIItem) -> None:
        """Add one labeled, exclusive button bound to a Viewer-state value."""
        title = item.get("title")
        state_path = item.get("state")
        command_id = item.get("command")
        if not isinstance(title, str) or not title:
            raise ValueError("State-bound toolbar buttons require a non-empty title.")
        if not isinstance(state_path, str) or not state_path:
            raise ValueError(f"State-bound toolbar button {title!r} requires a state path.")
        if not isinstance(command_id, str) or not command_id:
            raise ValueError(f"State-bound toolbar button {title!r} requires a command.")
        if "value" not in item:
            raise ValueError(f"State-bound toolbar button {title!r} requires a state value.")
        self.viewer.commands[command_id]
        value = item["value"]
        args = item.get("args") or []
        kwargs = item.get("kwargs") or {}
        component = Button(
            text=None if item.get("icon_only") else title,
            tooltip=item.get("tooltip") or title,
            icon_path=item.get("icon"),
            action=partial(self._invoke_state_button, command_id, args, kwargs),
        )
        button = component.widget
        button.setAccessibleName(title)
        button.setObjectName(f"toolbar_{state_path.replace('.', '_')}_{str(value)}")
        button.setCheckable(True)
        group = self._state_button_groups.get(state_path)
        if group is None:
            group = QButtonGroup(self.widget)
            group.setExclusive(True)
            self._state_button_groups[state_path] = group
        group.addButton(button)
        button.setChecked(self.viewer.state.get(state_path) == value)
        self._state_buttons.setdefault(state_path, []).append((button, value))
        self.widget.addWidget(button)

    def _invoke_state_button(self, command_id: str, args: list[Any], kwargs: dict[str, Any]) -> None:
        """Invoke one state-bound button command and restore viewport focus."""
        self.viewer.commands[command_id](*args, **kwargs)
        self._focus_restorer.request()

    def _set_renderer_focus(self) -> None:
        """Resolve the initialized renderer and give it interaction focus."""
        self.viewer.renderer.setFocus(Qt.FocusReason.OtherFocusReason)

    def _add_select(self, item: UIItem) -> None:
        """Add one labeled, state-bound selector to the toolbar."""
        title = item.get("title")
        state_path = item.get("state")
        options = item.get("items")
        if not isinstance(title, str) or not title:
            raise ValueError("Toolbar selectors require a non-empty title.")
        if not isinstance(state_path, str) or not state_path:
            raise ValueError(f"Toolbar selector {title!r} requires a state path.")
        if not isinstance(options, list) or not options:
            raise ValueError(f"Toolbar selector {title!r} requires at least one option.")

        selector = _ToolbarSelector()
        selector.setObjectName(f"toolbar_{state_path.replace('.', '_')}")
        values: list[object] = []
        for option in options:
            option_title = option.get("title")
            command_id = option.get("command")
            if not isinstance(option_title, str) or not option_title:
                raise ValueError(f"Toolbar selector {title!r} contains an option without a title.")
            if not isinstance(command_id, str) or not command_id:
                raise ValueError(f"Toolbar selector option {option_title!r} requires a command.")
            if "value" not in option:
                raise ValueError(f"Toolbar selector option {option_title!r} requires a state value.")
            self.viewer.commands[command_id]
            value = option["value"]
            values.append(value)
            selector.addItem(option_title, value)

        current = self.viewer.state.get(state_path)
        current_index = self._selector_index(title, values, current)
        selector.setCurrentIndex(current_index)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.addWidget(QLabel(title))
        layout.addWidget(selector)
        self.widget.addWidget(container)

        resolved_values = tuple(values)
        self._state_selectors.setdefault(state_path, []).append((selector, resolved_values))
        selector.currentIndexChanged.connect(partial(self._invoke_select, selector, options))
        selector.popup_hidden.connect(partial(self._focus_restorer.request, selector))

    def _invoke_select(self, selector: _ToolbarSelector, options: list[UIItem], index: int) -> None:
        """Invoke the existing command for one user-selected option."""
        if index < 0 or index >= len(options):
            return
        option = options[index]
        command_id = option.get("command")
        if not isinstance(command_id, str) or not command_id:
            raise ValueError("Toolbar selector options require a command.")
        command = self.viewer.commands[command_id]
        command(*(option.get("args") or []), **(option.get("kwargs") or {}))
        if not selector.popup_cycle_active:
            self._focus_restorer.request()

    def _on_state_changed(self, path: str, value: object) -> None:
        """Synchronize toolbar controls bound to a changed state path."""
        for selector, values in self._state_selectors.get(path, []):
            index = self._selector_index(selector.objectName(), values, value)
            selector.blockSignals(True)
            selector.setCurrentIndex(index)
            selector.blockSignals(False)
        buttons = self._state_buttons.get(path, [])
        group = self._state_button_groups.get(path)
        if group is not None:
            group.setExclusive(False)
        try:
            for button, button_value in buttons:
                button.setChecked(button_value == value)
        finally:
            if group is not None:
                group.setExclusive(True)

    @staticmethod
    def _selector_index(title: str, values: list[object] | tuple[object, ...], value: object) -> int:
        """Return the option index for a supported state value."""
        try:
            return values.index(value)
        except ValueError:
            raise ValueError(f"Toolbar selector {title!r} does not support state value {value!r}.") from None
