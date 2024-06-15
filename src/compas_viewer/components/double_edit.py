import sys

from PySide6 import QtWidgets


class DoubleEdit(QtWidgets.QWidget):
    """
    A custom QWidget for editing floating-point numbers with a label and a double spin box.

    Parameters
    ----------
    title : str, optional
        The label text to be displayed next to the spin box. Defaults to None.
    value : float, optional
        The initial value of the spin box. Defaults to None.
    min_val : float, optional
        The minimum value allowed in the spin box. Defaults to the smallest float value if not specified.
    max_val : float, optional
        The maximum value allowed in the spin box. Defaults to the largest float value if not specified.

    Attributes
    ----------
    layout : QHBoxLayout
        The horizontal layout containing the label and the spin box.
    label : QLabel
        The label displaying the title.
    spinbox : QDoubleSpinBox
        The double spin box for editing the floating-point number.

    Example
    -------
    >>> widget = DoubleEdit(title="X", value=0.0, min_val=-10.0, max_val=10.0)
    >>> widget.show()
    """

    def __init__(
        self,
        title: str = None,
        value: float = None,
        min_val: float = None,
        max_val: float = None,
    ):
        super().__init__()

        if min_val is None:
            min_val = -sys.float_info.max
        if max_val is None:
            max_val = sys.float_info.max

        self.layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(title)
        self.spinbox = QtWidgets.QDoubleSpinBox()
        self.spinbox.setMinimum(min_val)
        self.spinbox.setMaximum(max_val)
        self.spinbox.setValue(value)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spinbox)
        self.setLayout(self.layout)


class DoubleEditGroup(QtWidgets.QWidget):
    def __init__(
        self,
        title: str,
        settings: list[tuple[str, float, float, float]],
    ):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)

        self.group_box = QtWidgets.QGroupBox(title)
        group_layout = QtWidgets.QVBoxLayout()

        for setting in settings:
            widget = DoubleEdit(*setting)
            group_layout.addWidget(widget)

        group_layout.setSpacing(4)
        group_layout.setContentsMargins(4, 4, 4, 4)
        self.group_box.setLayout(group_layout)

        self.layout.addWidget(self.group_box)
        self.setLayout(self.layout)
