from collections.abc import Callable

from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QWidget

from .boundcomponent import BoundComponent
from .component import Component


class BooleanToggle(BoundComponent[bool]):
    """Create a labeled checkbox bound to a boolean value.
    (either a dictionary key or object attribute). When the checkbox state changes, it automatically
    updates the bound attribute and optionally calls a action function.

    Parameters
    ----------
    obj
        The object or dictionary containing the boolean attribute to be edited.
    attr
        The name of the attribute/key to be edited.
    title
        The label text to be displayed next to the checkbox. If None, uses the attr name.
    action
        A function to call when the checkbox state changes. Receives the component and new boolean value.

    Examples
    --------
    >>> class MyObject:
    ...     def __init__(self):
    ...         self.show_points = True
    >>> obj = MyObject()
    >>> component = BooleanToggle(obj, "show_points", title="Show Points")

    """

    def __init__(
        self,
        obj: object | dict[str, bool],
        attr: str,
        title: str | None = None,
        action: Callable[[Component, bool], None] | None = None,
    ) -> None:
        super().__init__(obj, attr, action=action)

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

        # Connect the checkbox state change signal to the action
        self.checkbox.stateChanged.connect(self.on_state_changed)

    def on_state_changed(self, state: int) -> None:
        """Update the bound value after the checkbox state changes.

        Parameters
        ----------
        state
            Qt checkbox state value.

        """
        # Convert Qt checkbox state to boolean
        is_checked = state == 2  # Qt.Checked = 2
        self.set_attr(is_checked)
        if self.action:
            self.action(self, is_checked)

    def sync_from_bound_object(self, value: bool) -> None:
        """Synchronize the checkbox without publishing another change."""
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(value)
        self.checkbox.blockSignals(False)
