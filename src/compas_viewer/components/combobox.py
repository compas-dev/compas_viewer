from typing import Callable
from typing import Optional

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


class ComboBox(QComboBox):
    """
    A customizable combo box widget, supporting item-specific rendering with an optional color delegate.

    Parameters
    ----------
    items : list
        List of items to populate the combo box.
    change_callback : Callable
        Function to execute on value change.
        Should accept a single argument corresponding to the selected item's data.
    paint : bool, optional
        Whether to use a custom delegate for item rendering, such as displaying colors. Defaults to None.

    Attributes
    ----------
    paint : bool
        Flag indicating whether custom item rendering is enabled.
    assigned_color : QColor or None
        The color assigned to the combo box before any changes.
    is_changed : bool
        Indicates if the color has been changed through user interaction.

    Methods
    -------
    populate(items: list) -> None
        Populates the combo box with items.
    setAssignedColor(color: QColor) -> None
        Sets the assigned color to be displayed when the item is not changed.
    on_index_changed(change_callback: Callable, index: int) -> None
        Handles the index change event and triggers the callback.
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
        paint: Optional[bool] = None,
    ):
        super().__init__()
        self.paint = paint
        self.assigned_color = None
        self.is_changed = False

        if self.paint:
            self.setItemDelegate(ColorDelegate())

        if items:
            self.populate(items)

        if change_callback:
            self.currentIndexChanged.connect(lambda index: self.on_index_changed(change_callback, index))

    def populate(self, items: list) -> None:
        """
        Populate the combo box with items.

        Parameters
        ----------
        items : list
            List of tuples, each containing the display text and user data
        """
        for item in items:
            if self.paint:
                self.addItem("", item)
                index = self.model().index(self.count() - 1, 0)
                self.model().setData(index, item, Qt.UserRole)
            else:
                self.addItem(item, item)

    def setAssignedColor(self, color: QColor) -> None:
        """
        Sets the assigned color to be displayed when the item is not changed.

        Parameters
        ----------
        color : QColor
            The color to be assigned to the combo box.
        """
        self.assigned_color = color

    def on_index_changed(self, change_callback: Callable, index: int) -> None:
        """
        Handles the index change event and triggers the callback.

        Parameters
        ----------
        change_callback : Callable
            Function to execute on value change.
        index : int
            The new index of the selected item.
        """
        self.is_changed = True
        change_callback(self.itemData(index))
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        rect = self.rect()

        color = self.currentData(Qt.UserRole) if self.is_changed else self.assigned_color

        if isinstance(color, QColor):
            painter.fillRect(rect, color)
        else:
            super().paintEvent(event)
        painter.end()


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
        # TODO: check _color attr ("double_edit", "G", obj.linecolor[0].g, 0, 1),
        default_color = getattr(self.obj, self.attr)
        default_color = QColor(*remap_rgb(default_color[0].rgb, to_range_one=False))

        self.layout = QVBoxLayout(self)
        self.color_selector = ComboBox(self.color_options, self.change_color, paint=True)
        self.color_selector.setAssignedColor(default_color)
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
