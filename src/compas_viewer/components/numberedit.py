from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QDoubleSpinBox
from typing import Callable
from typing import Union
from .component import Component
from .boundcomponent import BoundComponent


class NumberEdit(BoundComponent):
    """
    This component creates a labeled number spin box that can be bound to an object's attribute
    (either a dictionary key or object attribute). When the value changes, it automatically
    updates the bound attribute and optionally calls a callback function.

    Parameters
    ----------
    obj : Union[object, dict]
        The object or dictionary containing the attribute to be edited.
    attr : str
        The name of the attribute/key to be edited.
    title : str, optional
        The label text to be displayed next to the spin box. If None, uses the attr name.
    min_val : float, optional
        The minimum value allowed in the spin box. If None, uses the default minimum.
    max_val : float, optional
        The maximum value allowed in the spin box. If None, uses the default maximum.
    step : float, optional
        The step size for the spin box. Defaults to 0.1.
    decimals : int, optional
        The number of decimal places to display. Defaults to 1.
    callback : Callable[[Component, float], None], optional
        A function to call when the value changes. Receives the component and new value.

    Attributes
    ----------
    obj : Union[object, dict]
        The object or dictionary containing the attribute being edited.
    attr : str
        The name of the attribute/key being edited.
    callback : Callable[[Component, float], None] or None
        The callback function to call when the value changes.
    widget : QWidget
        The main widget containing the layout.
    layout : QHBoxLayout
        The horizontal layout containing the label and the spin box.
    label : QLabel
        The label displaying the title.
    spinbox : QDoubleSpinBox
        The double spin box for editing the floating-point number.

    Example
    -------
    >>> class MyObject:
    ...     def __init__(self):
    ...         self.x = 5.0
    >>> obj = MyObject()
    >>> component = NumberEdit(obj, "x", title="X Coordinate", min_val=0.0, max_val=10.0)
    """

    def __init__(
        self,
        obj: Union[object, dict],
        attr: str,
        title: str = None,
        min_val: float = None,
        max_val: float = None,
        step: float = 0.1,
        decimals: int = 1,
        callback: Callable[[Component, float], None] = None,
    ):
        super().__init__(obj, attr, callback=callback)

        self.widget = QWidget()
        self.layout = QHBoxLayout()

        title = title if title is not None else attr
        self.label = QLabel(title)
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setDecimals(decimals)
        self.spinbox.setSingleStep(step)
        self.spinbox.setMaximumSize(85, 25)

        self.spinbox.setValue(self.get_attr())

        if min_val is not None:
            self.spinbox.setMinimum(min_val)
        if max_val is not None:
            self.spinbox.setMaximum(max_val)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spinbox)
        self.widget.setLayout(self.layout)
        self.spinbox.valueChanged.connect(self.on_value_changed)
