from typing import Callable
from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QWidget

from .boundcomponent import BoundComponent
from .component import Component


class TextEdit(BoundComponent):
    """
    This component creates a labeled text edit widget that can be bound to an object's attribute
    (either a dictionary key or object attribute). When the text changes, it automatically
    updates the bound attribute and optionally calls a action function.

    Parameters
    ----------
    obj : Union[object, dict]
        The object or dictionary containing the attribute to be edited.
    attr : str
        The name of the attribute/key to be edited.
    title : str, optional
        The label text to be displayed next to the text edit. If None, uses the attr name.
    action : Callable[[Component, str], None], optional
        A function to call when the text changes. Receives the component and new text value.

    Attributes
    ----------
    obj : Union[object, dict]
        The object or dictionary containing the attribute being edited.
    attr : str
        The name of the attribute/key being edited.
    action : Callable[[Component, str], None] or None
        The action function to call when the text changes.
    widget : QWidget
        The main widget containing the layout.
    layout : QHBoxLayout
        The horizontal layout containing the label and the text edit.
    label : QLabel
        The label displaying the title.
    text_edit : QTextEdit
        The text edit widget for editing the text.

    Example
    -------
    >>> class MyObject:
    ...     def __init__(self):
    ...         self.name = "Hello World"
    >>> obj = MyObject()
    >>> component = TextEdit(obj, "name", title="Name")
    """

    def __init__(
        self,
        obj: Union[object, dict],
        attr: str,
        title: str = None,
        action: Callable[[Component, str], None] = None,
    ):
        super().__init__(obj, attr, action=action)

        self.widget = QWidget()
        self.layout = QHBoxLayout()

        title = title if title is not None else attr
        self.label = QLabel(title)
        self.text_edit = QTextEdit()
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit.setMaximumSize(85, 25)
        self.text_edit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.text_edit.setText(str(self.get_attr()))
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.text_edit)
        self.widget.setLayout(self.layout)

        # Connect the text change signal to the action
        self.text_edit.textChanged.connect(self.on_text_changed)

    def on_text_changed(self):
        """Handle text change events by updating the bound attribute and calling the action."""
        new_text = self.text_edit.toPlainText()
        self.on_value_changed(new_text)
