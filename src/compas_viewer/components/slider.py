from typing import Callable
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget


class Slider(QWidget):
    def __init__(
        self,
        title: str = "Slider",
        min_val: float = 0,
        max_val: float = 100,
        step: Optional[float] = 1,
        action: Callable = None,
        horizontal: Optional[bool] = True,
        starting_val: Optional[float] = None,
        tick_interval: Optional[float] = None,
    ):
        """
        A customizable slider widget for Qt applications, supporting both horizontal and vertical orientations. This
        widget displays the current, minimum, and maximum values and allows for dynamic user interaction.

        Parameters
        ----------
        title : str
            Label displayed above the slider, defaults to "Slider".
        min_val : float
            Minimum value of the slider, defaults to 0.
        max_val : float
            Maximum value of the slider, defaults to 100.
        step : float, optional
            Step size of the slider. Defaults to 1.
        action : Callable
            Function to execute on value change. Should accept a single integer argument.
        horizontal : bool, optional
            Orientation of the slider. True for horizontal, False for vertical. Defaults to True.
        starting_val : float, optional
            Initial value of the slider, defaults to the minimum value.
        tick_interval : float, optional
            Interval between tick marks. No ticks if None. Defaults to None.

        Attributes
        ----------
        title : str
            Label displayed above the slider.
        min_val : float
            Minimum value of the slider.
        max_val : float
            Maximum value of the slider.
        step : float
            Step size of the slider.
        action : Callable
            Function to execute on value change.
        start_val : float
            Initial value of the slider.
        layout : QVBoxLayout
            Layout of the widget.
        slider : QSlider
            Slider widget.
        value_label : QLabel
            Label displaying the current value of the slider.

        Example
        -------
        >>> slider = Slider("Brightness", min_val=0, max_val=255, starting_val=100)
        """
        super().__init__()
        self.title = title
        self.action = action
        self._horizontal = horizontal
        self.min_val = min_val
        self.max_val = max_val
        self.step = step or 1
        self.starting_val = starting_val if starting_val is not None else self.min_val
        self._tick_interval = tick_interval

        orientation = Qt.Horizontal if horizontal else Qt.Vertical

        if self.step:
            self.min_val /= step
            self.max_val /= step
            self._adjust_val = step
        else:
            self._adjust_val = 1

        if self._tick_interval is None:
            self._tick_interval: float = (self.max_val - self.min_val) / 10

        self.layout = QVBoxLayout(self)
        self._h_layout = QHBoxLayout()
        self.slider = QSlider(orientation)
        self.slider.setMinimum(self.min_val)
        self.slider.setMaximum(self.max_val)
        self.slider.setTickInterval(self._tick_interval)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setValue(self.starting_val)

        # Labels for displaying the range and current value
        self._min_label = QLabel(str(self.min_val * self._adjust_val), alignment=Qt.AlignLeft)
        self._max_label = QLabel(str(self.max_val * self._adjust_val), alignment=Qt.AlignRight)
        self.value_label = QLabel(f"{self.title}:")

        # Connect the slider movement to the callback
        self.slider.valueChanged.connect(self.on_value_changed)
        self.layout.addWidget(self.value_label)
        self.layout.addWidget(self.slider)

        # Add widgets to layout
        if orientation == Qt.Horizontal:
            self._h_layout.addWidget(self._min_label)
            self._h_layout.addWidget(self._max_label)
        else:
            self._h_layout.addWidget(self._min_label, 0, Qt.AlignTop)
            self._h_layout.addWidget(self._max_label, 0, Qt.AlignBottom)

        self.layout.addLayout(self._h_layout)

    def on_value_changed(self, value):
        """
        Update the label based on the slider's current value.
        """
        self.value_label.setText(f"{self.title}: {round(value*self._adjust_val,2)}")
        self.action(self, value * self._adjust_val)
