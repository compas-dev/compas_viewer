from collections.abc import Callable
from typing import TYPE_CHECKING
from typing import Generic
from typing import TypeVar
from typing import cast

from .component import Component

if TYPE_CHECKING:
    from compas_viewer.timer import Timer

T = TypeVar("T")


class BoundComponent(Component, Generic[T]):
    """Base class for components bound to an object attribute or dictionary key.

    This class provides common functionality for UI components that need to be bound
    to an attribute of an object or dictionary. It handles getting and setting values
    from the bound attribute and provides a action mechanism for when values change.

    Parameters
    ----------
    obj
        The object or dictionary containing the attribute to be bound.
    attr
        The name of the attribute/key to be bound.
    action
        A function to call when the value changes. Receives the component and new value.
    watch_interval
        Interval in milliseconds to check for changes in the bound object.
        If None, watching is disabled. Default is 100.

    """

    def __init__(
        self,
        obj: object | dict[str, T],
        attr: str | None,
        action: Callable[[Component, T], None] | None,
        watch_interval: int | None = 100,
    ) -> None:
        super().__init__()

        self.obj = obj
        self.attr = attr
        self.action = action
        self.watch_interval = watch_interval
        self._watch_timer: Timer | None = None
        self._last_watched_value: T | None = None
        self._updating_from_watch = False

        # Start watching if interval is provided
        if self.watch_interval is not None:
            self.start_watching()

    def get_attr(self) -> T | None:
        """Get the current value of the bound attribute.

        Returns
        -------
        T | None
            The current value of the attribute.

        """
        if self.obj is None or self.attr is None:
            return None
        if isinstance(self.obj, dict):
            return self.obj[self.attr]
        else:
            return getattr(self.obj, self.attr)

    def set_attr(self, value: T) -> None:
        """Set the value of the bound attribute.

        Parameters
        ----------
        value
            The new value to set.

        """
        if self.obj is None or self.attr is None:
            return
        if isinstance(self.obj, dict):
            self.obj[self.attr] = value
        else:
            setattr(self.obj, self.attr, value)

    def on_value_changed(self, value: T) -> None:
        """Handle value changes for the bound attribute.

        This method is called when the component's value changes. It updates the bound
        attribute and calls the action function if one was provided.

        Parameters
        ----------
        value
            The new value to set.

        """
        self.set_attr(value)
        if self.action is not None:
            self.action(self, value)

    def start_watching(self) -> None:
        """Start watching the bound object for changes.

        This method starts a timer that periodically checks if the bound attribute
        has changed and updates the component accordingly.
        """
        if self.watch_interval is None:
            return

        if self._watch_timer is not None:
            self.stop_watching()

        from compas_viewer.timer import Timer

        self._last_watched_value = self.get_attr()
        self._watch_timer = Timer(self.watch_interval, self._check_for_changes)

    def stop_watching(self) -> None:
        """Stop watching the bound object for changes."""
        if self._watch_timer is not None:
            self._watch_timer.stop()
            self._watch_timer = None

    def _check_for_changes(self) -> None:
        """
        Check if the bound attribute has changed and update the component if needed.

        This method is called periodically by the watch timer.
        """
        if self._updating_from_watch:
            return

        # Skip checking if widget is not visible to save resources
        if not self.widget.isVisible():
            return

        current_value = self.get_attr()
        if current_value != self._last_watched_value:
            self._last_watched_value = current_value
            self._updating_from_watch = True
            try:
                self.sync_from_bound_object(cast(T, current_value))
            finally:
                self._updating_from_watch = False

    def sync_from_bound_object(self, value: T) -> None:
        """Synchronize the component display with the bound value.

        This method should be overridden by subclasses to update their
        specific UI elements when the bound object changes.

        Parameters
        ----------
        value
            The new value from the bound object.

        """
        # Base implementation does nothing - subclasses should override
        pass

    def set_watch_interval(self, interval: int | None) -> None:
        """Set or disable the watch interval.

        Parameters
        ----------
        interval
            The new interval in milliseconds, or None to disable watching.

        """
        was_watching = self._watch_timer is not None

        if was_watching:
            self.stop_watching()

        self.watch_interval = interval

        if interval is not None:
            self.start_watching()
