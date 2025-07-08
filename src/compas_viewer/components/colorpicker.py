from typing import Callable
from typing import Union

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


def remap_rgb(value, to_range_one=True):
    """
    Remap an RGB value between the range (0, 255) and (0, 1).

    Parameters
    ----------
    value : tuple
        The RGB value to remap.
    to_range_one : bool, optional
        If True, remap from (0, 255) to (0, 1). If False, remap from (0, 1) to (0, 255).

    Returns
    -------
    tuple
        The remapped RGB value.
    """
    factor = 1 / 255 if to_range_one else 255
    return tuple(v * factor for v in value)


class ColorPicker(BoundComponent):
    """
    This component creates a labeled color picker button that can be bound to an object's color attribute
    (either a dictionary key or object attribute). When the color changes, it automatically
    updates the bound attribute and optionally calls a callback function.

    Parameters
    ----------
    obj : Union[object, dict]
        The object or dictionary containing the color attribute to be edited.
    attr : str
        The name of the attribute/key to be edited.
    title : str, optional
        The label text to be displayed next to the color picker. If None, uses the attr name.
    callback : Callable[[Component, Color], None], optional
        A function to call when the color changes. Receives the component and new color value.

    Attributes
    ----------
    obj : Union[object, dict]
        The object or dictionary containing the color attribute being edited.
    attr : str
        The name of the attribute/key being edited.
    callback : Callable[[Component, Color], None] or None
        The callback function to call when the color changes.
    widget : QWidget
        The main widget containing the layout.
    layout : QHBoxLayout
        The horizontal layout containing the label and the color picker button.
    label : QLabel
        The label displaying the title.
    color_button : QPushButton
        The button that displays the current color and opens the color dialog when clicked.
    current_color : QColor
        The currently selected color.

    Example
    -------
    >>> class MyObject:
    ...     def __init__(self):
    ...         self.color = Color(1.0, 0.0, 0.0)  # Red color
    >>> obj = MyObject()
    >>> component = ColorPicker(obj, "color", title="Object Color")
    """

    def __init__(
        self,
        obj: Union[object, dict],
        attr: str,
        title: str = None,
        callback: Callable[[Component, Color], None] = None,
    ):
        super().__init__(obj, attr, callback=callback)

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

    def open_color_dialog(self):
        """Opens a QColorDialog for the user to select a new color."""
        color = QColorDialog.getColor()

        if color.isValid():
            self.change_color(color)
            self.set_button_color(color)

    def set_button_color(self, color: QColor):
        """Sets the button's background and text to the provided color."""
        luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255
        if luminance < 0.5:
            self.color_button.setStyleSheet(f"background-color: {color.name()}; color: white;")
        else:
            self.color_button.setStyleSheet(f"background-color: {color.name()}; color: black;")
        self.color_button.setText(color.name())
        self.current_color = color

    def change_color(self, color: QColor):
        """Changes the color attribute of the object to the provided color and updates the object."""
        rgb = remap_rgb(color.getRgb())[:-1]  # rgba to rgb(0-1)
        new_color = Color(*rgb)
        self.on_value_changed(new_color)
