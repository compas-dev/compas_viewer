from abc import abstractmethod
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal

from compas_viewer.configurations import ActionConfig

from . import get_action_cls

if TYPE_CHECKING:
    from compas_viewer.viewer import Viewer


class Action(QObject):
    """
    Actions are functions that are called when a certain event happens, such as mouse and keyboard click.

    Parameters
    ----------
    name : str
        The name of the action. The key in the configuration dictionary should match the name.
    viewer : :class:`compas_viewer.viewer.Viewer`
        The viewer object.
    config : :class:`compas_viewer.configurations.controller_config.ActionConfig`
        The action configuration.

    Attributes
    ----------
    name : str
        The name of the action.
    viewer : :class:`compas_viewer.viewer.Viewer`
        The viewer object.
    config : :class:`compas_viewer.configurations.controller_config.ActionConfig`
        The action configuration.
    key : :QtCore:`PySide6.QtCore.Qt.Key`
        The key of the action.
    modifier : :QtCore:`PySide6.QtCore.Qt.KeyboardModifier`
        The modifier of the action.

    References
    ----------
    * https://doc.qt.io/qtforpython-6/PySide6/QtCore/Signal.html
    """

    pressed = Signal()
    released = Signal()

    def __new__(cls, name: str, viewer: "Viewer", config: ActionConfig, **kwargs):
        action_cls = get_action_cls(name)
        return super(Action, cls).__new__(action_cls, **kwargs)

    def __init__(self, name: str, viewer: "Viewer", config: ActionConfig):
        super(Action, self).__init__()
        self.name = name
        self.viewer = viewer
        self.config = config
        self.key = self.config.key
        self.modifier = self.config.modifier
        self.pressed.connect(self.pressed_action)
        self.released.connect(self.released_action)

    @abstractmethod
    def pressed_action(self):
        """
        The behavior of the action when the key is pressed.
        """
        self.viewer.renderer.update()

    @abstractmethod
    def released_action(self):
        """
        The behavior of the action when the key is released.
        """
        self.viewer.renderer.update()
