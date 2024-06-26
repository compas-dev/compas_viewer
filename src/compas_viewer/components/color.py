from typing import TYPE_CHECKING

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas.colors import Color
from compas.colors.colordict import ColorDict
from compas_viewer.base import Base
from compas_viewer.components.combobox import ComboBox

if TYPE_CHECKING:
    from compas_viewer.scene import ViewerSceneObject


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


class ColorComboBox(QWidget, Base):
    """
    A custom QWidget for selecting colors from a predefined list and applying the selected color to an object's attribute.

    Parameters
    ----------
    obj : ViewerSceneObject, optional
        The object to which the selected color will be applied. Defaults to None.
    attr : str, optional
        The attribute of the object to which the selected color will be applied. Defaults to None.

    Attributes
    ----------
    obj : ViewerSceneObject
        The object to which the selected color will be applied.
    attr : str
        The attribute of the object to which the selected color will be applied.
    color_options : list of QColor
        A list of predefined QColor objects representing available colors.
    layout : QVBoxLayout
        The layout of the widget.
    color_selector : ComboBox
        A combo box for selecting colors.

    Methods
    -------
    change_color(color: QColor) -> None
        Changes the color of the object's attribute to the selected color.

    Example
    -------
    >>> color_combobox = ColorComboBox(obj=some_obj, attr="linecolor")
    >>> color_combobox.show()
    """

    def __init__(
        self,
        obj: "ViewerSceneObject" = None,
        attr: str = None,
    ):
        super().__init__()
        self.obj = obj
        self.attr = attr

        self.color_options = [
            QColor(255, 255, 255),  # White
            QColor(211, 211, 211),  # LightGray
            QColor(190, 190, 190),  # Gray
            QColor(0, 0, 0),  # Black
            QColor(255, 0, 0),  # Red
            QColor(0, 255, 0),  # Green
            QColor(0, 0, 255),  # Blue
            QColor(255, 255, 0),  # Yellow
            QColor(0, 255, 255),  # Cyan
            QColor(255, 0, 255),  # Magenta
        ]

        default_color = getattr(self.obj, self.attr)

        if isinstance(default_color, Color):
            default_color = default_color.rgb
        elif isinstance(default_color, ColorDict):
            default_color = default_color.default
        else:
            raise ValueError("Invalid color type.")
        default_color = QColor(*remap_rgb(default_color, to_range_one=False))

        self.layout = QVBoxLayout(self)
        self.color_selector = ComboBox(self.color_options, self.change_color, paint=True)
        self.color_selector.setAssignedColor(default_color)
        self.layout.addWidget(self.color_selector)

    def change_color(self, color):
        rgb = remap_rgb(color.getRgb())[:-1]  # rgba to rgb(0-1)
        setattr(self.obj, self.attr, Color(*rgb))
        self.obj.update()


class ColorButton(QWidget):
    def __init__(
        self,
        obj: "ViewerSceneObject" = None,
        attr: str = None,
    ):
        super().__init__()

        self.obj = obj
        self.attr = attr

        default_color = getattr(self.obj, self.attr)
        if isinstance(default_color, Color):
            default_color = default_color.rgb
        elif isinstance(default_color, ColorDict):
            default_color = default_color.default
        else:
            raise ValueError("Invalid color type.")
        default_color = QColor(*remap_rgb(default_color, to_range_one=False))

        self.color_button = QPushButton(self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.color_button)
        self.color_button.clicked.connect(self.open_color_dialog)
        self.set_button_color(default_color)

    def open_color_dialog(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.change_color(color)
            self.set_button_color(color)

    def set_button_color(self, color: QColor):
        self.color_button.setStyleSheet(f"background-color: {color.name()};")
        self.color_button.setText(color.name())
        self.current_color = color

    def change_color(self, color):
        rgb = remap_rgb(color.getRgb())[:-1]  # rgba to rgb(0-1)
        setattr(self.obj, self.attr, Color(*rgb))
        self.obj.update()
