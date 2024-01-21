from typing import Callable
from typing import Optional

from compas.colors import Color
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QWidget


class Slider(QWidget):
    """Class representing a horizontal slider wrapped in a grid layout with two rows.

    Parameters
    ----------
    action : callable
        The callback connected to the slide action.
    value : int, optional
        The initial value of the slider.
        Defaults to 0.
    min_value : int, optional
        The minimum value of the sliding range.
        Defaults to 0.
    max_value : int, optional
        The maximum value of the sliding range.
        Defaults to 100.
    step : int, optional
        Size of value increments.
        Defaults to 1.
    title : str, optional
        Title label.
    annotation : str, optional
        Value annotation label.
    interval : int, optional
        The tick interval size.
        Defaults to 1.
    bgcolor : :class:`compas.colors.Color`, optional
        Background color of the box containing the slider.
    stretch : int, optional
        Stretch factor of the slider in the grid layout.
        Defaults to 0.
    kwargs : dict, optional
        Additional keyword arguments for the action.

    Attributes
    ----------
    action : callable
        Action associated with the button click event.
    slider : QtWidgets.QSlider
        The actual slider widget.
    value : float
        The current value of the slider.
    STYLE : str
        Stylesheet for the visual appearance of the groove and handle of the slider.

    See Also
    --------
    :class:`compas_viewer.layout.SidedockLayout`

    References
    ----------
    :PySide6:`PySide6/QtWidgets/QSlider`

    """

    STYLE = """
    QSlider::groove::horizontal {
        border: 1px solid #cccccc;
        background-color: #eeeeee;
        height: 4px;
    }
    QSlider::handle:horizontal {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 6px;
        height: 12px;
        width: 12px;
        margin: -6px 0;
    }
    """

    def __init__(
        self,
        action: Callable,
        value: int = 0,
        min_value: int = 0,
        max_value: int = 100,
        step: int = 1,
        title: Optional[str] = None,
        annotation: Optional[str] = None,
        interval: int = 1,
        bgcolor: Optional[Color] = None,
        stretch: int = 0,
        kwargs={},
    ):
        if min_value > max_value or interval > max_value - min_value:
            raise ValueError("Slider parameters are invalid. ")

        super().__init__()

        self.slider = QSlider()
        self._value = max(min(value, max_value), min_value)
        self.action = action
        self.stretch = stretch
        self.kwargs = kwargs

        # Row containing labels with horizontal box layout.
        row1 = QWidget()
        if bgcolor:
            row1.setStyleSheet("background-color: {}".format(bgcolor.hex))
        row1_layout = QHBoxLayout()
        row1_layout.setContentsMargins(12, 6, 12, 0)
        row1.setLayout(row1_layout)
        # The title label if provided
        if title:
            row1_layout.addWidget(QLabel(title))

        # The label containing the current value pushed to the right and potentially with an annotation.
        value_label = QLabel(str(self._value))
        row1_layout.addStretch(1)
        row1_layout.addWidget(value_label)
        if annotation:
            row1_layout.addWidget(QLabel(annotation))

        # Row containing slider
        row2 = QWidget()
        if bgcolor:
            row2.setStyleSheet("background-color: {}".format(bgcolor.hex))
        row2_layout = QHBoxLayout()
        row2_layout.setContentsMargins(12, 0, 12, 6)
        row2.setLayout(row2_layout)

        # Slider
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.slider.setMinimum(min_value)
        self.slider.setMaximum(max_value)
        self.slider.setValue(self._value)
        self.slider.setTickInterval(interval)
        self.slider.setSingleStep(step)
        self.slider.setStyleSheet(Slider.STYLE)
        row2_layout.addWidget(self.slider)

        # Combine rows in grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)
        grid_layout.addWidget(row1, 0, 0)
        grid_layout.addWidget(row2, 1, 0)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(grid_layout)

        # Connect slider to actions
        self.slider.valueChanged.connect(lambda v: value_label.setText(str(v)))
        self.slider.valueChanged.connect(self)

    def __call__(self, v):
        """Wrapper for the action associated with the slider.

        Returns
        -------
        None

        """
        return self.action(v, **self.kwargs)

    @property
    def value(self):
        return self.slider.value()

    @value.setter
    def value(self, value):
        self.slider.setValue(value)
