from typing import Callable
from typing import Union
from typing import Any
from .component import Component


class BoundComponent(Component):
    """
    Base class for components that are bound to object attributes.

    This class provides common functionality for UI components that need to be bound
    to an attribute of an object or dictionary. It handles getting and setting values
    from the bound attribute and provides a callback mechanism for when values change.

    Parameters
    ----------
    obj : Union[object, dict]
        The object or dictionary containing the attribute to be bound.
    attr : str
        The name of the attribute/key to be bound.
    callback : Callable[[Component, float], None]
        A function to call when the value changes. Receives the component and new value.

    Attributes
    ----------
    obj : Union[object, dict]
        The object or dictionary containing the attribute being bound.
    attr : str
        The name of the attribute/key being bound.
    callback : Callable[[Component, float], None]
        The callback function to call when the value changes.

    Example
    -------
    >>> class MyObject:
    ...     def __init__(self):
    ...         self.value = 10.0
    >>> def my_callback(component, value):
    ...     print(f"Value changed to: {value}")
    >>> obj = MyObject()
    >>> component = BoundComponent(obj, "value", my_callback)
    >>> component.set_attr(20.0)
    >>> print(component.get_attr())  # prints 20.0
    """
    
    def __init__(self, obj: Union[object, dict], attr: str, callback: Callable[[Component, float], None]):
        super().__init__()

        self.obj = obj
        self.attr = attr
        self.callback = callback

    def get_attr(self):
        """
        Get the current value of the bound attribute.

        Returns
        -------
        float
            The current value of the attribute.
        """
        if isinstance(self.obj, dict):
            return self.obj[self.attr]
        else:
            return getattr(self.obj, self.attr)

    def set_attr(self, value: float):
        """
        Set the value of the bound attribute.

        Parameters
        ----------
        value : float
            The new value to set.
        """
        if isinstance(self.obj, dict):
            self.obj[self.attr] = value
        else:
            setattr(self.obj, self.attr, value)

    def on_value_changed(self, value: Any):
        """
        Handle value changes for the bound attribute.

        This method is called when the component's value changes. It updates the bound
        attribute and calls the callback function if one was provided.

        Parameters
        ----------
        value : float
            The new value to set.
        """
        self.set_attr(value)
        if self.callback is not None:
            self.callback(self, value)
