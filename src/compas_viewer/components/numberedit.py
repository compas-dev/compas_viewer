from collections.abc import Callable
from typing import Any
from typing import cast

from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QWidget

from .boundcomponent import BoundComponent
from .component import Component


class NumberEdit(BoundComponent[float]):
    """Create a labeled spin box bound to a floating-point value.
    (either a dictionary key or object attribute). When the value changes, it automatically
    updates the bound attribute and optionally calls a action function.

    Parameters
    ----------
    obj
        The object or dictionary containing the attribute to be edited.
    attr
        The name of the attribute/key to be edited.
    title
        The label text to be displayed next to the spin box. If None, uses the attr name.
    min_val
        The minimum value allowed in the spin box. If None, uses the default minimum.
    max_val
        The maximum value allowed in the spin box. If None, uses the default maximum.
    step
        The step size for the spin box. Defaults to 0.1.
    decimals
        The number of decimal places to display. Defaults to 1.
    action
        A function to call when the value changes. Receives the component and new value.
    **kwargs
        Additional keyword arguments passed to BoundComponent, including:
        - `watch_interval`: interval in milliseconds, or `None` to disable watching.

    Examples
    --------
    >>> class MyObject:
    ...     def __init__(self):
    ...         self.x = 5.0
    >>> obj = MyObject()
    >>> # Component with default watcher (100ms)
    >>> component = NumberEdit(obj, "x", title="X Coordinate", min_val=0.0, max_val=10.0)
    >>> # Component without watcher
    >>> component = NumberEdit(obj, "x", title="X Coordinate", min_val=0.0, max_val=10.0, watch_interval=None)

    """

    def __init__(
        self,
        obj: object | dict[str, float],
        attr: str,
        title: str | None = None,
        min_val: float | None = None,
        max_val: float | None = None,
        step: float = 0.1,
        decimals: int = 1,
        action: Callable[[Component, float], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(obj, attr, action=action, **kwargs)

        self.widget = QWidget()
        self.layout = QHBoxLayout()

        title = title if title is not None else attr
        self.label = QLabel(title)
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setDecimals(decimals)
        self.spinbox.setSingleStep(step)
        self.spinbox.setMaximumSize(85, 25)

        self.spinbox.setValue(cast(float, self.get_attr()))

        if min_val is not None:
            self.spinbox.setMinimum(min_val)
        else:
            self.spinbox.setMinimum(-float("inf"))
        if max_val is not None:
            self.spinbox.setMaximum(max_val)
        else:
            self.spinbox.setMaximum(float("inf"))

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spinbox)
        self.widget.setLayout(self.layout)
        self.spinbox.valueChanged.connect(self.on_value_changed)

    def sync_from_bound_object(self, value: float) -> None:
        """Synchronize the spin box with the bound value.

        This method is called when the bound object's value changes externally.

        Parameters
        ----------
        value
            The new value from the bound object.

        """
        # Temporarily disconnect the signal to prevent infinite loops
        self.spinbox.valueChanged.disconnect(self.on_value_changed)
        try:
            self.spinbox.setValue(value)
        finally:
            # Reconnect the signal
            self.spinbox.valueChanged.connect(self.on_value_changed)
