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
        min_val: int = 0,
        max_val: int = 100,
        action: Callable = None,
        horizontal: Optional[bool] = True,
        step: Optional[float] = 1,
        tick_interval: Optional[float] = None,
        starting_val: Optional[float] = None,
    ):
        """
        A customizable slider widget for Qt applications, supporting both horizontal and vertical orientations. This
        widget displays the current, minimum, and maximum values and allows for dynamic user interaction.

        Parameters
        ----------
        title : str
            Label displayed above the slider, defaults to "Slider".
        min_val : int
            Minimum value of the slider, defaults to 0.
        max_val : int
            Maximum value of the slider, defaults to 100.
        action : Callable
            Function to execute on value change. Should accept a single integer argument.
        horizontal : bool, optional
            Orientation of the slider. True for horizontal, False for vertical. Defaults to True.
        step : float, optional
            Step size of the slider, defaults to 1.
        tick_interval : float, optional
            Interval between tick marks. No ticks if None. Defaults to None.
        starting_val : float, optional
            Initial value of the slider, defaults to the minimum value.

        Attributes
        ----------
        title : str
            Label displayed above the slider.
        min_val : int
            Minimum value of the slider.
        max_val : int
            Maximum value of the slider.
        action : Callable
            Function to execute on value change.

        Example
        -------
        >>> slider = Slider("Brightness", min_val=0, max_val=255, step=5)
        """
        super().__init__()

        self.title = title
        self.action = action
        self._horizontal = horizontal
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self._tick_interval = tick_interval
        self._starting_val = starting_val

        if self._horizontal:
            orientation = Qt.Horizontal
        else:
            orientation = Qt.Vertical

        if self._tick_interval is None:
            self._tick_interval = (self.max_val - self.min_val) / 10

        if self._starting_val is None:
            self._starting_val = self.min_val

        print(self.step)
        self.layout = QVBoxLayout(self)
        self.h_layout = QHBoxLayout()
        self.slider = QSlider(orientation)
        self.slider.setMinimum(self.min_val)
        self.slider.setMaximum(self.max_val)
        self.slider.setSingleStep(self.step)
        self.slider.setPageStep(self.step)

        self.slider.setTickInterval(self._tick_interval)
        self.slider.setTickPosition(QSlider.TicksBelow)

        self.slider.setValue(self._starting_val)

        # Labels for displaying the range and current value
        self.min_label = QLabel(str(self.min_val), alignment=Qt.AlignLeft)
        self.max_label = QLabel(str(self.max_val), alignment=Qt.AlignRight)
        self.value_label = QLabel(f"{self.title}: {self.slider.value()}")

        # Connect the slider movement to the callback
        self.slider.valueChanged.connect(self.on_value_changed)
        self.slider.valueChanged.connect(lambda value: self.action(value))
        self.layout.addWidget(self.value_label)

        # Add widgets to layout
        if orientation == Qt.Horizontal:
            self.h_layout.addWidget(self.min_label)
            self.h_layout.addWidget(self.max_label)
            self.layout.addWidget(self.slider)
            self.layout.addLayout(self.h_layout)
        else:
            self.layout.addWidget(self.slider)

    def on_value_changed(self, value):
        """
        Update the label based on the slider's current value.
        """
        self.value_label.setText(f"{self.title}: {value}")
