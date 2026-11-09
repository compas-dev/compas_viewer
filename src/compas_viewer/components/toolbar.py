from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QWidget

from compas_viewer.components import Button
from compas_viewer.components.component import Component
from compas_viewer.uidefinitions import UIItem

from .mainwindow import MainWindow


class ToolBar(Component):
    """Build the configured toolbar for a main window.

    Parameters
    ----------
    window
        Main window that owns the toolbar.

    """

    def __init__(self, window: MainWindow) -> None:
        super().__init__()
        self.widget = window.widget.addToolBar("Tools")
        self.widget.clear()
        self.widget.setMovable(False)
        self.widget.setObjectName("Tools")
        self._state_selectors: dict[str, list[tuple[QComboBox, tuple[object, ...]]]] = {}
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
                self.add_action(tooltip=tooltip, icon=icon, action=cast(Callable[..., object], action), args=args, kwargs=kwargs)
            elif itemtype == "action":
                self.add_action(text=text, action=cast(Callable[..., object], action), args=args, kwargs=kwargs)
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

        Returns
        -------
        QAction
            Toolbar action representing the button widget.

        """
        args = args or []
        kwargs = kwargs or {}
        button = Button(text=text, tooltip=tooltip, icon_path=icon, action=partial(action, *args, **kwargs))
        return self.widget.addWidget(button.widget)

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

        selector = QComboBox()
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
        selector.currentIndexChanged.connect(partial(self._invoke_select, options))

    def _invoke_select(self, options: list[UIItem], index: int) -> None:
        """Invoke the existing command for one user-selected option."""
        if index < 0 or index >= len(options):
            return
        option = options[index]
        command_id = option.get("command")
        if not isinstance(command_id, str) or not command_id:
            raise ValueError("Toolbar selector options require a command.")
        command = self.viewer.commands[command_id]
        command(*(option.get("args") or []), **(option.get("kwargs") or {}))

    def _on_state_changed(self, path: str, value: object) -> None:
        """Synchronize selectors bound to a changed Viewer-state path."""
        for selector, values in self._state_selectors.get(path, []):
            index = self._selector_index(selector.objectName(), values, value)
            selector.blockSignals(True)
            selector.setCurrentIndex(index)
            selector.blockSignals(False)

    @staticmethod
    def _selector_index(title: str, values: list[object] | tuple[object, ...], value: object) -> int:
        """Return the option index for a supported state value."""
        try:
            return values.index(value)
        except ValueError:
            raise ValueError(f"Toolbar selector {title!r} does not support state value {value!r}.") from None
