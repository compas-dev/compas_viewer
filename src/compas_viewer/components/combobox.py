from typing import Callable

from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas.colors import Color
from compas_viewer.base import Base


def remap_rgb(value):
    """Remap an RGB value from the range (0, 255) to (0, 1)."""
    return tuple(v / 255 for v in value)


class ComboBox(QComboBox):
    """
    A customizable combo box widget, supporting item-specific rendering with an optional color delegate.

    Parameters
    ----------
    items : list
        List of tuples, each containing the display text and user data.
    change_callback : Callable
        Function to execute on value change. Should accept a single argument corresponding to the selected item's data.
    paint : bool, optional
        Whether to use a custom delegate for item rendering, such as displaying colors. Defaults to None.

    Attributes
    ----------
    paint : bool
        Flag indicating whether custom item rendering is enabled.

    Methods
    -------
    populate(items: list) -> None
        Populates the combo box with items.
    paintEvent(event) -> None
        Custom painting for the combo box, used when `paint` is True.

    Example
    -------
    >>> items = [("Red", QColor(255, 0, 0)), ("Green", QColor(0, 255, 0)), ("Blue", QColor(0, 0, 255))]
    >>> combobox = ComboBox(items, change_callback=lambda x: print(x), paint=True)
    """

    def __init__(
        self,
        items: list = None,
        change_callback: Callable = None,
        paint: bool = None,
    ):
        super().__init__()

        self.paint = paint

        if self.paint:
            self.setItemDelegate(ColorDelegate())

        self.populate(items)
        self.currentIndexChanged.connect(lambda index: change_callback(self.itemData(index)))

    def populate(self, items: list) -> None:
        for item in items:
            if self.paint:
                self.addItem("", item)
                index = self.model().index(self.count() - 1, 0)
                self.model().setData(index, item, Qt.UserRole)
            else:
                self.addItem(item, item)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        rect = self.rect()

        # Draw the current selected color
        color = self.currentData(Qt.UserRole)
        if isinstance(color, QColor):
            painter.fillRect(rect, color)
        painter.end()


class ColorDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()

        # Get the color from the model data
        color = index.data(Qt.UserRole)
        if isinstance(color, QColor):
            # Draw the color rectangle
            painter.fillRect(option.rect, color)
        painter.restore()

    def sizeHint(self, option, index):
        # Set a fixed size for the items
        return QSize(100, 20)


class ColorComboBox(QWidget, Base):
    def __init__(self, obj, attr):
        super().__init__()
        self.obj = obj
        self.attr = attr

        self.color_options = [
            QColor(255, 255, 255),  # White
            QColor(211, 211, 211),  # LightGray
            QColor(0, 0, 0),  # Black
            QColor(255, 0, 0),  # Red
            QColor(0, 255, 0),  # Green
            QColor(0, 0, 255),  # Blue
            QColor(255, 255, 0),  # Yellow
            QColor(0, 255, 255),  # Cyan
            QColor(255, 0, 255),  # Magenta
        ]

        self.layout = QVBoxLayout(self)
        self.color_selector = ComboBox(self.color_options, self.change_color, paint=True)
        self.layout.addWidget(self.color_selector)

    def change_color(self, color):
        rgb = remap_rgb(color.getRgb())[:-1]  # rgba to rgb(0-1)
        setattr(self.obj, self.attr, Color(*rgb))


class ViewModeAction(QWidget, Base):
    def __init__(self):
        super().__init__()
        self.view_options = [
            "perspective",
            "top",
            "front",
            "right",
        ]

    def combobox(self):
        self.layout = QVBoxLayout(self)
        self.view_selector = ComboBox(self.view_options, self.change_view)
        self.layout.addWidget(self.view_selector)
        return self

    def change_view(self, mode):
        self.viewer.renderer.view = mode
