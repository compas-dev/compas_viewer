from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QCheckBox
from typing import Callable
from typing import Union
from .component import Component
from .boundcomponent import BoundComponent


class BooleanToggle(BoundComponent):
    """
    This component creates a labeled checkbox that can be bound to an object's boolean attribute
    (either a dictionary key or object attribute). When the checkbox state changes, it automatically
    updates the bound attribute and optionally calls a callback function.

    Parameters
    ----------
    obj : Union[object, dict]
        The object or dictionary containing the boolean attribute to be edited.
    attr : str
        The name of the attribute/key to be edited.
    title : str, optional
        The label text to be displayed next to the checkbox. If None, uses the attr name.
    callback : Callable[[Component, bool], None], optional
        A function to call when the checkbox state changes. Receives the component and new boolean value.

    Attributes
    ----------
    obj : Union[object, dict]
        The object or dictionary containing the boolean attribute being edited.
    attr : str
        The name of the attribute/key being edited.
    callback : Callable[[Component, bool], None] or None
        The callback function to call when the checkbox state changes.
    widget : QWidget
        The main widget containing the layout.
    layout : QHBoxLayout
        The horizontal layout containing the label and the checkbox.
    label : QLabel
        The label displaying the title.
    checkbox : QCheckBox
        The checkbox widget for toggling the boolean value.

    Example
    -------
    >>> class MyObject:
    ...     def __init__(self):
    ...         self.show_points = True
    >>> obj = MyObject()
    >>> component = BooleanToggle(obj, "show_points", title="Show Points")
    """

    def __init__(
        self,
        obj: Union[object, dict],
        attr: str,
        title: str = None,
        callback: Callable[[Component, bool], None] = None,
    ):
        super().__init__(obj, attr, callback=callback)

        self.widget = QWidget()
        self.layout = QHBoxLayout()

        title = title if title is not None else attr
        self.label = QLabel(title)
        self.checkbox = QCheckBox()
        self.checkbox.setMaximumSize(85, 25)

        # Set the initial state from the bound attribute
        initial_value = self.get_attr()
        if not isinstance(initial_value, bool):
            raise ValueError(f"Attribute '{attr}' must be a boolean value, got {type(initial_value)}")
        self.checkbox.setChecked(initial_value)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.checkbox)
        self.widget.setLayout(self.layout)

        # Connect the checkbox state change signal to the callback
        self.checkbox.stateChanged.connect(self.on_state_changed)

    def on_state_changed(self, state):
        """Handle checkbox state change events by updating the bound attribute and calling the callback."""
        # Convert Qt checkbox state to boolean
        is_checked = state == 2  # Qt.Checked = 2
        self.set_attr(is_checked)
        if self.callback:
            self.callback(self, is_checked)
