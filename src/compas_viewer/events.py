from typing import TYPE_CHECKING
from typing import Literal

from PySide6.QtCore import QObject
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QGestureEvent

if TYPE_CHECKING:
    from compas_viewer import Viewer


mousebutton_constant = {
    "LEFT": Qt.MouseButton.LeftButton,
    "RIGHT": Qt.MouseButton.RightButton,
    "MIDDLE": Qt.MouseButton.MiddleButton,
}


modifier_constant = {
    "CTRL": Qt.KeyboardModifier.ControlModifier,
    "SHIFT": Qt.KeyboardModifier.ShiftModifier,
    "ALT": Qt.KeyboardModifier.AltModifier,
}


class KeyEvent(QObject):
    """Class representing a key(board) event with a signal that can be registered to a slot by the event manager.

    Parameters
    ----------
    title : str
        The name of the command that is triggered by the event.
    key : str
        The string representation of the key that triggers the event.
    modifier : {'CTRL', 'SHIFT', 'ALT'}, optional
        The string representation of the modifier combined with the key.

    Attributes
    ----------
    title : str
        The name of the command that is triggered by the event.
    key : str
        The string representation of the key that triggers the event.
    keycode : int, readonly
        The unique numerical value corresponding to the key.
    modifier : Literal['CTRL', 'SHIFT', 'ALT'] | None, readonly
        The name of the modifier combined with the key.
    modifierconstant : Qt.KeyboardModifier, readonly
        The Qt type corresponding to the modifier.
    triggered : Signal, readonly
        The signal associated with the event.

    Examples
    --------
    >>> event = KeyEvent(title="Zoom Selected", key="F")
    >>> print(event)
    Zoom Selected: F

    """

    triggered = Signal()

    def __init__(self, title: str, key: str, modifier: Literal["CTRL", "SHIFT", "ALT"] = None) -> None:
        super().__init__()
        self._key = None
        self._keycode = None
        self._modifier = None
        self._modifierconstant = None
        self.title = title
        self.key = key
        self.modifier = modifier

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, name: str) -> None:
        self._key = name
        self._keycode = None
        for value in Qt.Key:
            if value.name == f"Key_{name}":
                self._keycode = value

    @property
    def keycode(self) -> int:
        return self._keycode

    @property
    def modifier(self) -> str:
        return self._modifier

    @modifier.setter
    def modifier(self, name: str) -> None:
        self._modifier = name
        self._modifierconstant = None
        if not name:
            self._modifierconstant = Qt.KeyboardModifier.NoModifier
        else:
            self._modifierconstant = modifier_constant[name]

    @property
    def modifierconstant(self) -> Qt.KeyboardModifier:
        return self._modifierconstant

    def __str__(self):
        if self.modifier:
            return f"{self.title}: {self.key} + {self.modifier}"
        return f"{self.title}: {self.key}"

    def __eq__(self, event: QKeyEvent) -> bool:
        return event.key() == self.keycode and event.modifiers() == self.modifierconstant


class MouseEvent(QObject):
    """Class representing a mouse event with a signal that can be registered to a slot by the event manager.

    Parameters
    ----------
    title : str
        The name of the command that is triggered by the mouse.
    button : {'LEFT', 'RIGHT', 'MIDDLE'}
        The string representation of the button that triggers the event.
    modifier : {'CTRL', 'SHIFT', 'ALT'}, optional
        The string representation of the modifier combined with the button.

    Attributes
    ----------
    title : str
        The name of the command that is triggered by the mouse.
    button : {'LEFT', 'RIGHT', 'MIDDLE'}
        The string representation of the mouse button.
    buttonconstant : int, readonly
        The unique numerical value corresponding to the key.
    modifier : Literal['CTRL', 'SHIFT', 'ALT'] | None, readonly
        The name of the modifier combined with the button.
    modifierconstant : Qt.KeyboardModifier, readonly
        The Qt type corresponding to the modifier.
    triggered : Signal, readonly
        The signal associated with the event.

    Examples
    --------
    >>> event = MouseEvent(title="Pan View", button="RIGHT", modifier="SHIFT")
    >>> print(event)
    Pan View: RIGHT + SHIFT

    """

    triggered = Signal(QMouseEvent)

    def __init__(self, title, button, modifier, context=None):
        super().__init__()
        self._button = None
        self._buttonconstant = None
        self._modifier = None
        self._modifierconstant = None
        self.title = title
        self.button = button
        self.modifier = modifier
        self.context = context
        self.is_active = False

    @property
    def button(self) -> str:
        return self._button

    @button.setter
    def button(self, name: str) -> None:
        self._button = name
        self._buttonconstant = mousebutton_constant[name]

    @property
    def buttonconstant(self) -> Qt.MouseButton:
        return self._buttonconstant

    @property
    def modifier(self) -> str:
        return self._modifier

    @modifier.setter
    def modifier(self, name: str) -> None:
        self._modifier = name
        self._modifierconstant = None
        if not name:
            self._modifierconstant = Qt.KeyboardModifier.NoModifier
        else:
            self._modifierconstant = modifier_constant[name]

    @property
    def modifierconstant(self) -> Qt.KeyboardModifier:
        return self._modifierconstant

    def __str__(self):
        if self.modifier:
            return f"{self.title}: {self.button} + {self.modifier}"
        return f"{self.title}: {self.button}"

    def __eq__(self, event: QMouseEvent) -> bool:
        return event.buttons() == self._buttonconstant and event.modifiers() == self._modifierconstant


class WheelEvent(QObject):
    """Class representing a wheel event with a signal that can be registered to a slot by the event manager.

    Parameters
    ----------
    title : str
        The name of the command that is triggered by the wheel.

    Attributes
    ----------
    title : str
        The name of the command that is triggered by the wheel.
    triggered : Signal, readonly
        The signal associated with the event.

    Examples
    --------
    >>> event = WheelEvent(title="Zoom View")
    >>> print(event)
    Zoom View

    """

    triggered = Signal(QWheelEvent)

    def __init__(self, title):
        super().__init__()
        self.title = title

    def __str__(self):
        return f"{self.title}"


class EventManager:
    """Class representing a manager for user inout events.

    Parameters
    ----------
    viewer : :class:`compas_viewer.Viewer`
        The parent viewer of the event manager.

    Attributes
    ----------
    key_events : list[:class:`KeyEvent`]
        The registered key events.
    mouse_events : list[:class:`MouseEvent`]
        The registered mouse events.
    wheel_events : list[:class:`WheelEvent`]
        The registered wheel events.

    """

    def __init__(self, viewer: "Viewer") -> None:
        self.viewer = viewer
        self.key_events: list[KeyEvent] = []
        self.mouse_events: list[MouseEvent] = []
        self.wheel_events: list[WheelEvent] = []
        self.register_bindings()

    def register_bindings(self):
        for cmd in self.viewer.config.commands:
            if cmd.mousebinding is not None:
                binding = cmd.mousebinding.split("+")
                button = binding[0].strip()
                modifier = None
                if len(binding) > 1:
                    modifier = binding[1].strip()
                mouseevent = MouseEvent(title=cmd.title, button=button, modifier=modifier)
                mouseevent.triggered.connect(cmd)
                self.mouse_events.append(mouseevent)

            if cmd.keybinding is not None:
                binding = cmd.keybinding.split("+")
                key = binding[0].strip()
                modifier = None
                if len(binding) > 1:
                    modifier = binding[1].strip()
                keyevent = KeyEvent(title=cmd.title, key=key, modifier=modifier)
                keyevent.triggered.connect(cmd)
                self.key_events.append(keyevent)

            if cmd.wheelbinding is not None:
                binding = cmd.wheelbinding.split("+")
                wheelevent = WheelEvent(title=cmd.title)
                wheelevent.triggered.connect(cmd)
                self.wheel_events.append(wheelevent)

    def delegate_keypress(self, event: QKeyEvent):
        for keyevent in self.key_events:
            if keyevent == event:
                keyevent.triggered.emit()
                break

    def delegate_keyrelease(self, event: QKeyEvent):
        pass

    def delegate_mousepress(self, event: QMouseEvent):
        self.viewer.mouse.last_pos = event.pos()
        for mouseevent in self.mouse_events:
            if mouseevent == event:
                mouseevent.triggered.emit(event)
                mouseevent.is_active = True
                break

    def delegate_mousemove(self, event: QMouseEvent):
        self.viewer.mouse.pos = event.pos()
        for mouseevent in self.mouse_events:
            if mouseevent == event:
                mouseevent.triggered.emit(event)
                break
        self.viewer.mouse.last_pos = event.pos()

    def delegate_mouserelease(self, event: QMouseEvent):
        for mouseevent in self.mouse_events:
            if mouseevent.is_active or mouseevent == event:
                mouseevent.triggered.emit(event)
                mouseevent.is_active = False
                break
        self.viewer.mouse.last_pos = event.pos()

    def delegate_wheel(self, event: QWheelEvent):
        for wheelevent in self.wheel_events:
            wheelevent.triggered.emit(event)

    def delegate_pinch(self, event: QGestureEvent):
        pass
