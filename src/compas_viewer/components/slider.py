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
        horizontal: Optional[bool] = True,
        min_val: float = 0,
        max_val: float = 100,
        action: Callable = None,
        tick_interval: Optional[float] = None,
        starting_val: Optional[float] = None,
    ):
        """
        Initialize the slider with labels to display its state.

        :param orientation: Qt.Horizontal or Qt.Vertical for slider orientation.
        :param min_val: The minimum value of the slider.
        :param max_val: The maximum value of the slider.
        :param change_callback: A function to call when the slider value changes.
        :param tick_interval: The interval between ticks displayed on the slider (optional).
        :param starting_val: The starting value of the slider (optional).
        """
        super().__init__()

        self.title = title

        if horizontal:
            orientation = Qt.Horizontal
        else:
            orientation = Qt.Vertical

        self.layout = QVBoxLayout(self)
        self.h_layout = QHBoxLayout()
        self.slider = QSlider(orientation)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)

        if tick_interval is not None:
            self.slider.setTickInterval(tick_interval)
            self.slider.setTickPosition(QSlider.TicksBelow)

        if starting_val is not None:
            self.slider.setValue(starting_val)
        else:
            self.slider.setValue(min_val)  # Default to minimum if not specified

        # Labels for displaying the range and current value
        self.min_label = QLabel(str(min_val), alignment=Qt.AlignLeft)
        self.max_label = QLabel(str(max_val), alignment=Qt.AlignRight)
        self.value_label = QLabel(f"{self.title}: {self.slider.value()}")

        # Connect the slider movement to the callback
        self.slider.valueChanged.connect(self.on_value_changed)
        self.slider.valueChanged.connect(lambda value: action(value))
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
