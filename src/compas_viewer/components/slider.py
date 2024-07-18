from typing import Callable
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas_viewer.components.textedit import TextEdit


class Slider(QWidget):
    def __init__(
        self,
        title: str = "Slider",
        min_val: float = 0,
        max_val: float = 100,
        step: Optional[float] = 1,
        action: Callable = None,
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
        self.min_val = min_val
        self.max_val = max_val
        self.step = step or 1
        self.starting_val = starting_val if starting_val is not None else self.min_val
        self._tick_interval = tick_interval if tick_interval is not None else (self._scaled_max_val - self._scaled_min_val) / 10

        self._updating = False

        self._default_layout = None
        self.layout = self.default_layout

        self._text_layout = QHBoxLayout()
        self._domain_layout = QHBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(self._scaled_min_val)
        self.slider.setMaximum(self._scaled_max_val)
        self.slider.setTickInterval(self._tick_interval)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setValue(self.starting_val)
        # Connect the slider movement to the callback
        self.slider.valueChanged.connect(self.on_value_changed)

        # Labels for displaying the range and current value
        self._min_label = QLabel(str(self.min_val), alignment=Qt.AlignLeft)
        self._max_label = QLabel(str(self.max_val), alignment=Qt.AlignRight)
        self.value_label = QLabel(f"{self.title}:")
        self.text_edit = TextEdit(str(self.starting_val))
        self.text_edit.text_edit.textChanged.connect(self.text_update)

        self._text_layout.addWidget(self.value_label)
        self._text_layout.addWidget(self.text_edit.text_edit)

        # Add widgets to layout
        self._domain_layout.addWidget(self._min_label)
        self._domain_layout.addWidget(self._max_label)

        self.layout.addLayout(self._text_layout)
        self.layout.addWidget(self.slider)
        self.layout.addLayout(self._domain_layout)
        self.setLayout(self.layout)

    @property
    def default_layout(self):
        if self._default_layout is None:
            from compas_viewer.components.layout import DefaultLayout

            self._default_layout = DefaultLayout(QVBoxLayout())
        return self._default_layout

    @property
    def _scaled_min_val(self):
        return self.min_val / self.step

    @property
    def _scaled_max_val(self):
        return self.max_val / self.step

    def on_value_changed(self, value):
        if self._updating:
            return
        self._updating = True
        scaled_value = round(value * self.step, 2)
        self.text_edit.text_edit.setText(str(scaled_value))
        if self.action:
            self.action(self, scaled_value)
        self._updating = False

    def text_update(self):
        if self._updating:
            return
        self._updating = True
        try:
            value = float(self.text_edit.text_edit.toPlainText()) / self.step
            self.slider.setValue(value)
            if self.action:
                self.action(self, value * self.step)
        except ValueError:
            pass  # Handle cases where the text is not a valid number
        self._updating = False
