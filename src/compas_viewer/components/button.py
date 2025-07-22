import pathlib
from typing import Callable
from typing import Optional
from typing import Union

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from .component import Component


def set_icon_path(icon_name: str) -> str:
    path = QtGui.QIcon(str(pathlib.Path(__file__).parent.parent / "assets" / "icons" / icon_name))
    return path


class Button(Component):
    """
    This component creates a button widget that can be customized with text, icon, tooltip, and action.

    Parameters
    ----------
    text : str, optional
        The text to display on the button.
    icon_path : Union[str, pathlib.Path], optional
        The path to the icon file to display on the button.
    tooltip : str, optional
        The tooltip text to show when hovering over the button.
    action : Callable[[], None], optional
        A function to call when the button is clicked.

    Attributes
    ----------
    widget : QPushButton
        The push button widget.
    action : Callable[[], None] or None
        The callback function to call when the button is clicked.

    Example
    -------
    >>> def my_action():
    ...     print("Button clicked!")
    >>> component = Button(text="Click Me", action=my_action)
    """

    def __init__(
        self,
        text: Optional[str] = None,
        icon_path: Optional[Union[str, pathlib.Path]] = None,
        tooltip: Optional[str] = None,
        action: Optional[Callable[[], None]] = None,
    ):
        super().__init__()

        self.action = action
        self.widget = QtWidgets.QPushButton()

        if text:
            self.widget.setText(text)
        if icon_path:
            self.widget.setIcon(QtGui.QIcon(set_icon_path(icon_path)))
            self.widget.setIconSize(QtCore.QSize(17, 17))
        if tooltip:
            self.widget.setToolTip(tooltip)
        if action:
            self.widget.clicked.connect(action)
