from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast

from PySide6.QtGui import QAction

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
            # elif itemtype == "select":
            #     self.add_combobox(item["items"], item["action"])
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
        return self.widget.addWidget(Button(text=text, tooltip=tooltip, icon_path=icon, action=partial(action, *args, **kwargs)))

    # def add_combobox(self, items, action, title=None):
    #     combobox = QComboBox()
    #     for item in items:
    #         combobox.addItem(item["title"], item.get("value", item["title"]))
    #     combobox.currentIndexChanged.connect(lambda index: action(combobox.itemData(index)))
    #     self.widget.addWidget(combobox)
