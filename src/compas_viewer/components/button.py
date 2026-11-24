from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QEvent
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QPushButton

from .component import Component


class _PaletteButton(QPushButton):
    """Refresh a monochrome icon when the application palette changes."""

    def __init__(self) -> None:
        super().__init__()
        self._icon_path: str | Path | None = None

    def set_palette_icon(self, icon_path: str | Path) -> None:
        """Set the source icon and render it with the current palette."""
        self._icon_path = icon_path
        self.setIcon(set_icon_path(icon_path))

    def changeEvent(self, event: QEvent) -> None:  # noqa: N802
        """Retint the source icon after an application palette change."""
        super().changeEvent(event)
        if event.type() == QEvent.Type.PaletteChange and self._icon_path is not None:
            self.setIcon(set_icon_path(self._icon_path))


def set_icon_path(icon_name: str | Path) -> QIcon:
    """Create a palette-tinted icon from the viewer's icon directory.

    Parameters
    ----------
    icon_name
        Icon filename relative to the viewer icon directory.

    Returns
    -------
    QIcon
        Icon tinted with the active and disabled button-text colors.

    """
    icon_path = Path(__file__).resolve().parent.parent / "assets" / "icons" / icon_name
    source = QIcon(str(icon_path))
    icon = QIcon()
    for group, mode in (
        (QPalette.ColorGroup.Active, QIcon.Mode.Normal),
        (QPalette.ColorGroup.Disabled, QIcon.Mode.Disabled),
    ):
        pixmap = source.pixmap(QSize(64, 64))
        tint = QPainter(pixmap)
        tint.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        tint.fillRect(pixmap.rect(), QApplication.palette().color(group, QPalette.ColorRole.ButtonText))
        tint.end()
        icon.addPixmap(pixmap, mode)
    return icon


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
        self.widget = _PaletteButton()

        if text:
            self.widget.setText(text)
        if icon_path:
            self.widget.set_palette_icon(icon_path)
            self.widget.setIconSize(QSize(17, 17))
        if tooltip:
            self.widget.setToolTip(tooltip)
        if action:
            self.widget.clicked.connect(action)
