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

from compas_viewer.base import Base


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
