from PySide6.QtCore import QObject

from .action import Action


class ZoomSelected(Action, QObject):
    """Look at action."""

    def pressed_action(self):
        raise NotImplementedError
