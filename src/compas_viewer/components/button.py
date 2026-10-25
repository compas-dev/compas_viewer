from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton

from .component import Component


def set_icon_path(icon_name: str | Path) -> QIcon:
    """Create an icon from the viewer's icon directory.

    Parameters
    ----------
    icon_name
        Icon filename relative to the viewer icon directory.

    Returns
    -------
    QIcon
        The loaded Qt icon.

    """
    icon_path = Path(__file__).resolve().parent.parent / "assets" / "icons" / icon_name
    return QIcon(str(icon_path))


class Button(Component):
    """Create a push button with optional text, icon, tooltip, and callback.

    Parameters
    ----------
    text
        The text to display on the button.
    icon_path
        The path to the icon file to display on the button.
    tooltip
        The tooltip text to show when hovering over the button.
    action
        A function to call when the button is clicked.

    Examples
    --------
    >>> def my_action():
    ...     print("Button clicked!")
    >>> component = Button(text="Click Me", action=my_action)

    """

    def __init__(
        self,
        text: str | None = None,
        icon_path: str | Path | None = None,
        tooltip: str | None = None,
        action: Callable[[], object] | None = None,
    ) -> None:
        super().__init__()

        self.action = action
        self.widget = QPushButton()

        if text:
            self.widget.setText(text)
        if icon_path:
            self.widget.setIcon(set_icon_path(icon_path))
            self.widget.setIconSize(QSize(17, 17))
        if tooltip:
            self.widget.setToolTip(tooltip)
        if action:
            self.widget.clicked.connect(action)
