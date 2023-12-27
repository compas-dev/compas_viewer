from typing import TYPE_CHECKING

from compas_viewer.configurations import ControllerConfig
from compas_viewer.utilities import supported_keys

if TYPE_CHECKING:
    from compas_viewer.viewer import Viewer


class Controller:
    """
    The Controller class is the main entry of all the key and mouse events.
    It is used to manage actions and events in the viewer.

    Parameters
    ----------
    viewer : :class:`compas_viewer.Viewer`
        The viewer object.
    config : :class:`compas_viewer.configurations.ControllerConfig`
        The controller configuration.

    Attributes
    ----------
    viewer : :class:`compas_viewer.Viewer`
        The viewer object.
    config : :class:`compas_viewer.configurations.ControllerConfig`
        The controller configuration.
    supported_keys : dict[str, any]
        The supported keys.
    """

    def __init__(self, viewer: "Viewer", config: ControllerConfig):
        self.viewer = viewer
        self.config = config
        self.supported_keys = supported_keys

    def mouse_move_action(self, event):
        """
        The mouse move action.

        Parameters
        ----------
        event : :class:`PySide2.QtGui.QMouseEvent`
            The Qt event.
        """
        raise NotImplementedError

    def mouse_press_action(self, event):
        """
        The mouse press action.

        Parameters
        ----------
        event : :class:`PySide2.QtGui.QMouseEvent`
            The Qt event.
        """
        raise NotImplementedError

    def mouse_release_action(self, event):
        """
        The mouse release action.

        Parameters
        ----------
        event : :class:`PySide2.QtGui.QMouseEvent`
            The Qt event.
        """
        raise NotImplementedError

    def wheel_action(self, event):
        """
        The wheel action.

        Parameters
        ----------
        event : :class:`PySide2.QtGui.QWheelEvent`
            The Qt event.
        """
        raise NotImplementedError

    def key_press_action(self, event):
        """
        The key press action.

        Parameters
        ----------
        event : :class:`PySide2.QtGui.QKeyEvent`
            The Qt event.
        """
        raise NotImplementedError

    def key_release_action(self, event):
        """
        The key release action.

        Parameters
        ----------
        event : :class:`PySide2.QtGui.QKeyEvent`
            The Qt event.
        """
        raise NotImplementedError
