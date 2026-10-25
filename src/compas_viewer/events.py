from typing import TYPE_CHECKING
from typing import Literal
from typing import cast

from PySide6.QtCore import QObject
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QGestureEvent

from compas_viewer.base import Base

if TYPE_CHECKING:
    from compas_viewer.commands import Command

type ModifierName = Literal["CTRL", "SHIFT", "ALT"]
type MouseButtonName = Literal["LEFT", "RIGHT", "MIDDLE"]


mousebutton_constant: dict[MouseButtonName, Qt.MouseButton] = {
    "LEFT": Qt.MouseButton.LeftButton,
    "RIGHT": Qt.MouseButton.RightButton,
    "MIDDLE": Qt.MouseButton.MiddleButton,
}


modifier_constant: dict[ModifierName, Qt.KeyboardModifier] = {
    "CTRL": Qt.KeyboardModifier.ControlModifier,
    "SHIFT": Qt.KeyboardModifier.ShiftModifier,
    "ALT": Qt.KeyboardModifier.AltModifier,
}


class KeyEvent(QObject):
    """Represent a keyboard binding registered with the event manager.

    Parameters
    ----------
    title
        The name of the command that is triggered by the event.
    key
        The string representation of the key that triggers the event.
    modifier
        The string representation of the modifier combined with the key.

    Examples
    --------
    >>> event = KeyEvent(title="Zoom Selected", key="F")
    >>> print(event)
    Zoom Selected: F

    """

    triggered = Signal()

    def __init__(self, title: str, key: str, modifier: ModifierName | None = None) -> None:
        super().__init__()
        self._key: str
        self._keycode: Qt.Key | None
        self._modifier: ModifierName | None
        self._modifierconstant: Qt.KeyboardModifier
        self.title = title
        self.key = key
        self.modifier = modifier

    @property
    def key(self) -> str:
        """str: The key name used by the binding."""
        return self._key

    @key.setter
    def key(self, name: str) -> None:
        self._key = name
        self._keycode = None
        for value in Qt.Key:
            if value.name == f"Key_{name}":
                self._keycode = value

    @property
    def keycode(self) -> Qt.Key | None:
        """Qt.Key | None: The corresponding Qt key value."""
        return self._keycode

    @property
    def modifier(self) -> ModifierName | None:
        """ModifierName | None: The modifier combined with the key."""
        return self._modifier

    @modifier.setter
    def modifier(self, name: ModifierName | None) -> None:
        self._modifier = name
        if not name:
            self._modifierconstant = Qt.KeyboardModifier.NoModifier
        else:
            self._modifierconstant = modifier_constant[name]

    @property
    def modifierconstant(self) -> Qt.KeyboardModifier:
        """Qt.KeyboardModifier: The corresponding Qt modifier value."""
        return self._modifierconstant

    def __str__(self) -> str:
        if self.modifier:
            return f"{self.title}: {self.key} + {self.modifier}"
        return f"{self.title}: {self.key}"

    def __eq__(self, event: QKeyEvent) -> bool:
        return event.key() == self.keycode and event.modifiers() == self.modifierconstant


class MouseEvent(QObject):
    """Represent a mouse binding registered with the event manager.

    Parameters
    ----------
    title
        The name of the command that is triggered by the mouse.
    button
        The string representation of the button that triggers the event.
    modifier
        The string representation of the modifier combined with the button.

    Examples
    --------
    >>> event = MouseEvent(title="Pan View", button="RIGHT", modifier="SHIFT")
    >>> print(event)
    Pan View: RIGHT + SHIFT

    """

    triggered = Signal(QMouseEvent)

    def __init__(self, title: str, button: MouseButtonName, modifier: ModifierName | None, context: object | None = None) -> None:
        super().__init__()
        self._button: MouseButtonName
        self._buttonconstant: Qt.MouseButton
        self._modifier: ModifierName | None
        self._modifierconstant: Qt.KeyboardModifier
        self.title = title
        self.button = button
        self.modifier = modifier
        self.context = context
        self.is_active = False

    @property
    def button(self) -> MouseButtonName:
        """MouseButtonName: The button name used by the binding."""
        return self._button

    @button.setter
    def button(self, name: MouseButtonName) -> None:
        self._button = name
        self._buttonconstant = mousebutton_constant[name]

    @property
    def buttonconstant(self) -> Qt.MouseButton:
        """Qt.MouseButton: The corresponding Qt mouse-button value."""
        return self._buttonconstant

    @property
    def modifier(self) -> ModifierName | None:
        """ModifierName | None: The modifier combined with the button."""
        return self._modifier

    @modifier.setter
    def modifier(self, name: ModifierName | None) -> None:
        self._modifier = name
        if not name:
            self._modifierconstant = Qt.KeyboardModifier.NoModifier
        else:
            self._modifierconstant = modifier_constant[name]

    @property
    def modifierconstant(self) -> Qt.KeyboardModifier:
        """Qt.KeyboardModifier: The corresponding Qt modifier value."""
        return self._modifierconstant

    def __str__(self) -> str:
        if self.modifier:
            return f"{self.title}: {self.button} + {self.modifier}"
        return f"{self.title}: {self.button}"

    def __eq__(self, event: QMouseEvent) -> bool:
        return event.buttons() == self._buttonconstant and event.modifiers() == self._modifierconstant


class WheelEvent(QObject):
    """Represent a wheel binding registered with the event manager.

    Parameters
    ----------
    title
        The name of the command that is triggered by the wheel.

    Examples
    --------
    >>> event = WheelEvent(title="Zoom View")
    >>> print(event)
    Zoom View

    """

    triggered = Signal(QWheelEvent)

    def __init__(self, title: str) -> None:
        super().__init__()
        self.title = title

    def __str__(self) -> str:
        return f"{self.title}"


class EventManager(Base):
    """Register viewer input bindings and dispatch matching Qt events."""

    def __init__(self) -> None:
        self.key_events: list[KeyEvent] = []
        self.mouse_events: list[MouseEvent] = []
        self.wheel_events: list[WheelEvent] = []
        self.register_bindings()

    def register_bindings(self) -> None:
        for cmd in self.viewer.commands:
            self.register_command(cmd)

    def reload_bindings(self) -> None:
        """Rebuild all input bindings from the runtime command registry."""
        self.key_events.clear()
        self.mouse_events.clear()
        self.wheel_events.clear()
        self.register_bindings()

    def register_command(self, command: "Command") -> None:
        """Register the input bindings declared by a runtime command.

        Parameters
        ----------
        command
            Command whose keyboard, mouse, and wheel bindings should be added.

        """
        if command.mousebinding is not None:
            binding = command.mousebinding.split("+")
            button = cast(MouseButtonName, binding[0].strip())
            modifier: ModifierName | None = None
            if len(binding) > 1:
                modifier = cast(ModifierName, binding[1].strip())
            mouseevent = MouseEvent(title=command.title, button=button, modifier=modifier)
            mouseevent.triggered.connect(command)
            self.mouse_events.append(mouseevent)

        if command.keybinding is not None:
            binding = command.keybinding.split("+")
            key = binding[0].strip()
            modifier = None
            if len(binding) > 1:
                modifier = cast(ModifierName, binding[1].strip())
            keyevent = KeyEvent(title=command.title, key=key, modifier=modifier)
            keyevent.triggered.connect(command)
            self.key_events.append(keyevent)

        if command.wheelbinding is not None:
            wheelevent = WheelEvent(title=command.title)
            wheelevent.triggered.connect(command)
            self.wheel_events.append(wheelevent)

    def delegate_keypress(self, event: QKeyEvent) -> None:
        """Dispatch a key-press event to matching bindings.

        Parameters
        ----------
        event
            Qt key event to dispatch.

        """
        for keyevent in self.key_events:
            if keyevent == event:
                keyevent.triggered.emit()

    def delegate_keyrelease(self, event: QKeyEvent) -> None:
        """Handle a key-release event.

        Parameters
        ----------
        event
            Qt key event to dispatch.

        """
        pass

    def delegate_mousepress(self, event: QMouseEvent) -> None:
        """Dispatch a mouse-press event to matching bindings.

        Parameters
        ----------
        event
            Qt mouse event to dispatch.

        """
        self.viewer.mouse.begin(event.pos())
        for mouseevent in self.mouse_events:
            if mouseevent == event:
                mouseevent.triggered.emit(event)
                mouseevent.is_active = True

    def delegate_mousemove(self, event: QMouseEvent) -> None:
        """Dispatch a mouse-move event to matching bindings.

        Parameters
        ----------
        event
            Qt mouse event to dispatch.

        """
        self.viewer.mouse.pos = event.pos()
        for mouseevent in self.mouse_events:
            if mouseevent == event:
                mouseevent.triggered.emit(event)

        self.viewer.mouse.last_pos = event.pos()

    def delegate_mouserelease(self, event: QMouseEvent) -> None:
        """Dispatch a mouse-release event to matching bindings.

        Parameters
        ----------
        event
            Qt mouse event to dispatch.

        """
        for mouseevent in self.mouse_events:
            if mouseevent.is_active or mouseevent == event:
                mouseevent.triggered.emit(event)
                mouseevent.is_active = False

        self.viewer.mouse.end(event.pos())

    def delegate_wheel(self, event: QWheelEvent) -> None:
        """Dispatch a wheel event to registered bindings.

        Parameters
        ----------
        event
            Qt wheel event to dispatch.

        """
        for wheelevent in self.wheel_events:
            wheelevent.triggered.emit(event)

    def delegate_pinch(self, event: QGestureEvent) -> None:
        """Handle a pinch gesture event.

        Parameters
        ----------
        event
            Qt gesture event to dispatch.

        """
        pass
