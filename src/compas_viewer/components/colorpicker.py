from collections.abc import Callable
from collections.abc import Sequence

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QWidget

from compas.colors import Color
from compas.colors.colordict import ColorDict

from .boundcomponent import BoundComponent
from .component import Component


def remap_rgb(value: Sequence[float], to_range_one: bool = True) -> tuple[float, ...]:
    """Remap RGB channels between the ranges 0–255 and 0–1.

    Parameters
    ----------
    value
        The RGB value to remap.
    to_range_one
        If True, remap from (0, 255) to (0, 1). If False, remap from (0, 1) to (0, 255).

    Returns
    -------
    tuple[float, ...]
        The remapped RGB value.

    """
    factor = 1 / 255 if to_range_one else 255
    return tuple(v * factor for v in value)


class ColorPicker(BoundComponent[Color]):
    """Create a labeled color picker bound to a COMPAS color value.
    (either a dictionary key or object attribute). When the color changes, it automatically
    updates the bound attribute and optionally calls a action function.

    Parameters
    ----------
    obj
        The object or dictionary containing the color attribute to be edited.
    attr
        The name of the attribute/key to be edited.
    title
        The label text to be displayed next to the color picker. If None, uses the attr name.
    action
        A function to call when the color changes. Receives the component and new color value.

    Examples
    --------
    >>> class MyObject:
    ...     def __init__(self):
    ...         self.color = Color(1.0, 0.0, 0.0)  # Red color
    >>> obj = MyObject()
    >>> component = ColorPicker(obj, "color", title="Object Color")

    """

    def __init__(
        self,
        obj: object | dict[str, Color],
        attr: str,
        title: str | None = None,
        action: Callable[[Component, Color], None] | None = None,
    ) -> None:
        super().__init__(obj, attr, action=action)

        self.widget = QWidget()
        self.layout = QHBoxLayout()

        title = title if title is not None else attr
        self.label = QLabel(title)
        self.color_button = QPushButton()
        self.color_button.setMaximumSize(85, 25)

        # Get the initial color from the bound attribute
        default_color = self.get_attr()
        if isinstance(default_color, Color):
            default_color = default_color.rgb
        elif isinstance(default_color, ColorDict):
            default_color = default_color.default
        else:
            raise ValueError("Invalid color type. : {}".format(type(default_color)))

        default_color = QColor(*remap_rgb(default_color, to_range_one=False))
        self.current_color = default_color

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.color_button)
        self.widget.setLayout(self.layout)

        self.color_button.clicked.connect(self.open_color_dialog)
        self.set_button_color(default_color)

    def open_color_dialog(self) -> None:
        """Open a color dialog and apply a valid selection."""
        color = QColorDialog.getColor()

        if color.isValid():
            self.change_color(color)
            self.set_button_color(color)

    def set_button_color(self, color: QColor) -> None:
        """Update the button styling for a Qt color.

        Parameters
        ----------
        color
            Color used for the button background and contrast-aware text.

        """
        luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255
        if luminance < 0.5:
            self.color_button.setStyleSheet(f"background-color: {color.name()}; color: white;")
        else:
            self.color_button.setStyleSheet(f"background-color: {color.name()}; color: black;")
        self.color_button.setText(color.name())
        self.current_color = color

    def change_color(self, color: QColor) -> None:
        """Update the bound COMPAS color from a Qt color.

        Parameters
        ----------
        color
            Qt color selected by the user.

        """
        rgb = remap_rgb(color.getRgb())[:-1]  # rgba to rgb(0-1)
        new_color = Color(red=rgb[0], green=rgb[1], blue=rgb[2])
        self.on_value_changed(new_color)

    def sync_from_bound_object(self, value: Color) -> None:
        """Synchronize the button with a changed COMPAS color."""
        self.set_button_color(QColor(*remap_rgb(value.rgb, to_range_one=False)))
