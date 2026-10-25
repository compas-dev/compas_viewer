from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QWidget

from .boundcomponent import BoundComponent
from .component import Component


class TextEdit(BoundComponent[str]):
    """Create a labeled text editor bound to a string value.
    (either a dictionary key or object attribute). When the text changes, it automatically
    updates the bound attribute and optionally calls a action function.

    Parameters
    ----------
    obj
        The object or dictionary containing the attribute to be edited.
    attr
        The name of the attribute/key to be edited.
    title
        The label text to be displayed next to the text edit. If None, uses the attr name.
    action
        A function to call when the text changes. Receives the component and new text value.

    Examples
    --------
    >>> class MyObject:
    ...     def __init__(self):
    ...         self.name = "Hello World"
    >>> obj = MyObject()
    >>> component = TextEdit(obj, "name", title="Name")

    """

    def __init__(
        self,
        obj: object | dict[str, str],
        attr: str,
        title: str | None = None,
        action: Callable[[Component, str], None] | None = None,
    ) -> None:
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

    def on_text_changed(self) -> None:
        """Handle text change events by updating the bound attribute and calling the action."""
        new_text = self.text_edit.toPlainText()
        self.on_value_changed(new_text)
