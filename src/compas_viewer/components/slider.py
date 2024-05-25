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
        starting_val: Optional[int] = None,
        tick_interval: Optional[int] = None,
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
        starting_val : int, optional
            Initial value of the slider, defaults to the minimum value.
        tick_interval : float, optional
            Interval between tick marks. No ticks if None. Defaults to None.

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
        start_val : int
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
        # TODO(pitsai): add step method
        self.title = title
        self.action = action
        self._horizontal = horizontal
        self.min_val = min_val
        self.max_val = max_val
        self.starting_val = starting_val
        self._tick_interval = tick_interval

        if self._horizontal:
            orientation = Qt.Horizontal
        else:
            orientation = Qt.Vertical

        if self._tick_interval is None:
            self._tick_interval = (self.max_val - self.min_val) / 10

        if self.starting_val is None:
            self.starting_val = self.min_val

        self.layout = QVBoxLayout(self)
        self._h_layout = QHBoxLayout()
        self.slider = QSlider(orientation)
        self.slider.setMinimum(self.min_val)
        self.slider.setMaximum(self.max_val)

        self.slider.setTickInterval(self._tick_interval)
        self.slider.setTickPosition(QSlider.TicksBelow)

        self.slider.setValue(self.starting_val)

        # Labels for displaying the range and current value
        self._min_label = QLabel(str(self.min_val), alignment=Qt.AlignLeft)
        self._max_label = QLabel(str(self.max_val), alignment=Qt.AlignRight)
        self.value_label = QLabel(f"{self.title}: {self.slider.value()}")

        # Connect the slider movement to the callback
        self.slider.valueChanged.connect(self.on_value_changed)
        self.slider.valueChanged.connect(lambda value: self.action(self, value))
        self.layout.addWidget(self.value_label)

        # Add widgets to layout
        if orientation == Qt.Horizontal:
            self._h_layout.addWidget(self._min_label)
            self._h_layout.addWidget(self._max_label)
            self.layout.addWidget(self.slider)
            self.layout.addLayout(self._h_layout)
        else:
            self.layout.addWidget(self.slider)

    def on_value_changed(self, value):
        """
        Update the label based on the slider's current value.
        """
        self.value_label.setText(f"{self.title}: {value}")
