from functools import partial
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication

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


class KeyboardShortcut(QObject):
    triggered = Signal()

    def __init__(self, title, key, modifier, context=None):
        super().__init__()
        self._key = None
        self._keycode = None
        self._modifier = None
        self._modifierconstant = None
        self.title = title
        self.key = key
        self.modifier = modifier
        self.context = context

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

    def __str__(self):
        if self.modifier:
            return f"{self.title}: {self.key} + {self.modifier}"
        return f"{self.title}: {self.key}"

    def __eq__(self, event: QKeyEvent) -> bool:
        return event.key() == self._keycode and event.modifiers() == self._modifierconstant


class MouseEvent(QObject):
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

    @property
    def button(self) -> str:
        return self._button

    @button.setter
    def button(self, name: str) -> None:
        self._button = name
        self._buttonconstant = mousebutton_constant[name]

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

    def __str__(self):
        if self.modifier:
            return f"{self.title}: {self.button} + {self.modifier}"
        return f"{self.title}: {self.button}"

    def __eq__(self, event: QMouseEvent) -> bool:
        return event.buttons() == self._buttonconstant and event.modifiers() == self._modifierconstant


class WheelEvent(QObject):
    triggered = Signal(QWheelEvent)

    def __init__(self, title):
        super().__init__()
        self.title = title


class EventManager:

    def __init__(self, viewer: "Viewer") -> None:
        self.viewer = viewer
        self.shortcuts: list[KeyboardShortcut] = []
        self.mouseevents: list[MouseEvent] = []
        self.wheelevents: list[WheelEvent] = []
        self.register_keyboard_shortcuts()
        self.register_mouseevents()
        self.register_wheelevents()

    def register_keyboard_shortcuts(self):
        for item in self.viewer.config.keyboard_shortcuts.items:
            title = item["title"]
            key = item["key"]
            modifier = item["modifier"]
            slot = item["action"]
            shortcut = KeyboardShortcut(title=title, key=key, modifier=modifier)
            shortcut.triggered.connect(slot)
            self.shortcuts.append(shortcut)

    def register_mouseevents(self):
        for item in self.viewer.config.mouse_events.items:
            title = item["title"]
            button = item["button"]
            modifier = item["modifier"]
            slot = item["action"]
            mouseevent = MouseEvent(title=title, button=button, modifier=modifier)
            mouseevent.triggered.connect(partial(slot, self.viewer))
            self.mouseevents.append(mouseevent)

    def register_wheelevents(self):
        for item in self.viewer.config.wheel_events.items:
            wheelevent = WheelEvent(title=item["title"])
            wheelevent.triggered.connect(partial(item["action"], self.viewer))
            self.wheelevents.append(wheelevent)

    def delegate_keypress(self, event: QKeyEvent):
        for shortcut in self.shortcuts:
            if shortcut == event:
                shortcut.triggered.emit()
                break

    def delegate_keyrelease(self, event: QKeyEvent):
        pass

    def delegate_mousemove(self, event: QMouseEvent):
        self.viewer.mouse.pos = event.pos()
        for mouseevent in self.mouseevents:
            if mouseevent == event:
                mouseevent.triggered.emit(event)
                break
        self.viewer.mouse.last_pos = event.pos()

    def delegate_mousepress(self, event: QMouseEvent):
        self.viewer.mouse.last_pos = event.pos()
        for mouseevent in self.mouseevents:
            if mouseevent == event:
                mouseevent.triggered.emit(event)
                break

    def delegate_mouserelease(self, event: QMouseEvent):
        for mouseevent in self.mouseevents:
            if mouseevent == event:
                mouseevent.triggered.emit(event)
                break
        self.viewer.mouse.last_pos = event.pos()
        QApplication.restoreOverrideCursor()

    def delegate_wheel(self, event: QWheelEvent):
        for wheelevent in self.wheelevents:
            wheelevent.triggered.emit(event)
