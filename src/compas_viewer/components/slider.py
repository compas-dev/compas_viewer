from collections.abc import Callable
from typing import Any
from typing import cast

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from .boundcomponent import BoundComponent
from .component import Component


class Slider(BoundComponent[float]):
    """Create a numeric slider bound to a value or used standalone.
    (either a dictionary key or object attribute). When the value changes, it automatically
    updates the bound attribute and optionally calls a action function.

    Parameters
    ----------
    obj
        The object or dictionary containing the attribute to be edited. If None, the slider
        operates with the provided value parameter.
    attr
        The name of the attribute/key to be edited. If None, the slider operates with the
        provided value parameter.
    value
        The initial value for the slider when not bound to an object attribute. Defaults to 0.
    title
        Label displayed above the slider. If None, uses the attr name or "Value" if attr is None.
    min_val
        Minimum value of the slider. Defaults to 0.
    max_val
        Maximum value of the slider. Defaults to 100.
    step
        Step size of the slider. Defaults to 1.
    tick_interval
        Interval between tick marks. No ticks if None. Defaults to None.
    action
        A function to call when the value changes. Receives the component and new value.
    **kwargs
        Additional keyword arguments passed to BoundComponent, including:
        - `watch_interval`: interval in milliseconds, or `None` to disable watching.

    Examples
    --------
    >>> # Bound to an object attribute
    >>> class MyObject:
    ...     def __init__(self):
    ...         self.brightness = 50.0
    >>> obj = MyObject()
    >>> def my_action(component, value):
    ...     print(f"Brightness changed to: {value}")
    >>> component = Slider(obj, "brightness", title="Brightness", min_val=0, max_val=100, action=my_action)

    >>> # Standalone slider with initial value
    >>> standalone_slider = Slider(value=25.0, title="Volume", min_val=0, max_val=100)

    """

    def __init__(
        self,
        obj: object | dict[str, float] | None = None,
        attr: str | None = None,
        value: float = 0,
        title: str | None = None,
        min_val: float = 0,
        max_val: float = 100,
        step: float = 1,
        tick_interval: float | None = None,
        action: Callable[[Component, float], None] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(obj, attr, action=action, **kwargs)

        self.title = title if title is not None else (attr if attr is not None else "Value")
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self._tick_interval = tick_interval if tick_interval is not None else (self._scaled_max_val - self._scaled_min_val) / 10

        self._updating = False

        # Determine the initial value consistently
        if obj is not None and attr is not None:
            initial_value = cast(float, self.get_attr())
        else:
            initial_value = value

        # Clamp initial value to valid range
        initial_value = max(self.min_val, min(self.max_val, initial_value))

        # Create the main widget and layout
        self.widget = QWidget()
        self.layout = QVBoxLayout()

        self._text_layout = QHBoxLayout()
        self._domain_layout = QHBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(self._scaled_min_val)
        self.slider.setMaximum(self._scaled_max_val)
        self.slider.setTickInterval(self._tick_interval)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setValue(self._scale_value(initial_value))
        # Connect the slider movement to the action
        self.slider.valueChanged.connect(self.on_slider_changed)

        # Labels for displaying the range and current value
        self._min_label = QLabel(str(self.min_val), alignment=Qt.AlignLeft)
        self._max_label = QLabel(str(self.max_val), alignment=Qt.AlignRight)
        self.value_label = QLabel(f"{self.title}:")
        self.line_edit = QLineEdit(str(initial_value))
        self.line_edit.setMaximumSize(85, 25)
        self.line_edit.textChanged.connect(self.on_text_changed)

        self._text_layout.addWidget(self.value_label)
        self._text_layout.addWidget(self.line_edit)

        # Add widgets to layout
        self._domain_layout.addWidget(self._min_label)
        self._domain_layout.addWidget(self._max_label)

        self.layout.addLayout(self._text_layout)
        self.layout.addWidget(self.slider)
        self.layout.addLayout(self._domain_layout)
        self.widget.setLayout(self.layout)

    @property
    def _scaled_min_val(self) -> int:
        return int(self.min_val / self.step)

    @property
    def _scaled_max_val(self) -> int:
        return int(self.max_val / self.step)

    def _scale_value(self, value: float) -> int:
        """Scale a real value to slider integer value."""
        return round(value / self.step)

    def _unscale_value(self, scaled_value: int) -> float:
        """Unscale a slider integer value to real value."""
        return round(scaled_value * self.step, 2)

    def on_slider_changed(self, scaled_value: int) -> None:
        """Handle a slider value change.

        Parameters
        ----------
        scaled_value
            Integer slider value to convert to the configured numeric range.

        """
        if self._updating:
            return
        self._updating = True
        real_value = self._unscale_value(scaled_value)
        self.line_edit.setText(str(real_value))
        self.on_value_changed(real_value)
        self._updating = False

    def on_text_changed(self) -> None:
        """Handle text input changes."""
        if self._updating:
            return
        self._updating = True
        try:
            value = float(self.line_edit.text())
            # Clamp value to valid range
            clamped_value = max(self.min_val, min(self.max_val, value))

            # Update the line edit if the value was clamped
            if clamped_value != value:
                self.line_edit.setText(str(clamped_value))

            self.slider.setValue(self._scale_value(clamped_value))
            self.on_value_changed(clamped_value)
        except ValueError:
            pass  # Handle cases where the text is not a valid number
        self._updating = False

    def sync_from_bound_object(self, value: float) -> None:
        """Synchronize the slider and text input with the bound value.

        This method is called when the bound object's value changes externally.

        Parameters
        ----------
        value
            The new value from the bound object.

        """
        if self._updating:
            return

        self._updating = True
        try:
            # Clamp value to valid range
            clamped_value = max(self.min_val, min(self.max_val, value))

            # Update both the slider and the text input
            self.slider.setValue(self._scale_value(clamped_value))
            self.line_edit.setText(str(clamped_value))
        finally:
            self._updating = False
