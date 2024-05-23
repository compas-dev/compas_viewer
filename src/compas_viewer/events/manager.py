from typing import TYPE_CHECKING

from PySide6.QtCore import QObject
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QKeyEvent

# from PySide6.QtGui import QMouseEvent

if TYPE_CHECKING:
    from compas_viewer import Viewer


modifier_code = {
    "CTRL": Qt.KeyboardModifier.ControlModifier,
    "SHIFT": Qt.KeyboardModifier.ShiftModifier,
}


class KeyboardShortcut(QObject):
    pressed = Signal()
    released = Signal()

    def __init__(self, title, key, modifier, context=None):
        super().__init__()
        self._key = None
        self._keycode = None
        self._modifier = None
        self._modifiercode = None
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
    def modifier(self, name: str | None) -> None:
        self._modifier = name
        self._modifiercode = None
        if not name:
            self._modifiercode = Qt.KeyboardModifier.NoModifier
        else:
            self._modifiercode = modifier_code[name]

    def __str__(self):
        if self.modifier:
            return f"{self.title}: {self.key} + {self.modifier}"
        return f"{self.title}: {self.key}"

    def __eq__(self, event: QKeyEvent) -> bool:
        return event.key() == self._keycode and event.modifiers() == self._modifiercode


class EventManager:

    def __init__(self, viewer: "Viewer") -> None:
        self.viewer = viewer
        self.keyboard_shortcuts: list[KeyboardShortcut] = []
        self.register_keyboard_shortcuts()

    def register_keyboard_shortcuts(self):
        for item in self.viewer.config.keyboard_shortcuts.items:
            title = item["title"]
            key = item["key"]
            modifier = item["modifier"]
            slot = item["action"]
            shortcut = KeyboardShortcut(title=title, key=key, modifier=modifier)
            shortcut.pressed.connect(slot)
            self.keyboard_shortcuts.append(shortcut)

    def delegate_keypress(self, event: QKeyEvent):
        for shortcut in self.keyboard_shortcuts:
            if shortcut == event:
                shortcut.pressed.emit()

    def delegate_keyrelease(self, event: QKeyEvent):
        print("NotImplementedError")

    # def delegate_mousemove(self, event: QMouseEvent):
    #     pass

    # def delegate_mousepress(self, event: QMouseEvent):
    #     pass

    # def delegate_mouserelease(self, event: QMouseEvent):
    #     pass
