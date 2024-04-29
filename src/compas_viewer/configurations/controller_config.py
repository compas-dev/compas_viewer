from pathlib import Path
from typing import Union

from PySide6.QtCore import Qt

from compas_viewer import HERE
from compas_viewer.qt import key_mapper

from .config import Config


class ActionConfig:
    """
    The class representation  of the key-based action configuration.
    The action config contains two elements, "key" and "modifier".

    Parameters
    ----------
    key : str
        The key.
    modifier : str, optional
        The key modifier.

    Attributes
    ----------
    config : :class:`ActionConfigType`
        A TypedDict with defined keys and types.
    key : :QtCore:`PySide6.QtCore.Qt.Key`
        The Qt key.
    modifier : :QtCore:`PySide6.QtCore.Qt.KeyboardModifier`
        The Qt modifier.

    See Also
    --------
    :class:`compas_viewer.configurations.controller_config.ControllerConfig`
    """

    def __init__(self, key: str, modifier: str = "no"):
        self.key = key_mapper(key, 0)
        self.modifier = key_mapper(modifier, 1)


class MouseConfig:
    """
    The class representation of the mouse-based movement configuration.
    The mouse contains two elements, "mouse" and "modifier".

    Parameters
    ----------
    mouse : str
        The mouse button.
    modifier : str, optional
        The key modifier.

    Attributes
    ----------
    config : :class:`MouseConfigType`
        A TypedDict with defined keys and types.
    mouse : :QtCore:`PySide6.QtCore.Qt.MouseButton`
        The Qt mouse.
    modifier : :QtCore:`PySide6.QtCore.Qt.KeyboardModifier`
        The Qt modifier.

    See Also
    --------
    :class:`compas_viewer.configurations.controller_config.ControllerConfig`
    """

    def __init__(self, mouse: str, modifier: str = "no"):
        self.mouse = key_mapper(mouse, 2)
        self.modifier = key_mapper(modifier, 1)


class ControllerConfig(Config):
    """
    The class representation for the `controller.json` of
    the class Controller.
    The controller.json contains all the settings about controlling the viewer: mouse, keys, ...

    Parameters
    ----------
    pan : Union[tuple[str, str],tuple[str]]
        The mouse and modifier for panning the view.
    rotate : Union[tuple[str, str],tuple[str]]
        The mouse and modifier for rotating the view.
    drag_selection : Union[tuple[str, str],tuple[str]]
        The mouse and modifier for dragging to select objects.
    drag_deselection : Union[tuple[str, str],tuple[str]]
        The mouse and modifier for dragging to deselect objects.
    multiselect : Union[tuple[str, str],tuple[str]]
        The mouse and modifier for multiselecting objects.
    deselect : Union[tuple[str, str],tuple[str]]
        The mouse and modifier for deselecting objects.
    actions : dict[str, Union[tuple[str, str],tuple[str]]]
        The key and modifier for the actions.

    See Also
    --------
    :class:`compas_viewer.components.controller.Controller`
    """

    def __init__(
        self,
        pan: Union[tuple[str, str], tuple[str]],
        rotate: Union[tuple[str, str], tuple[str]],
        drag_selection: Union[tuple[str, str], tuple[str]],
        drag_deselection: Union[tuple[str, str], tuple[str]],
        multiselect: Union[tuple[str, str], tuple[str]],
        deselect: Union[tuple[str, str], tuple[str]],
        actions: dict[str, Union[tuple[str, str], tuple[str]]],
    ):
        super().__init__()
        # Zoom function fixed.
        self.zoom = None
        # Select function fixed.
        self.select = Qt.MouseButton.LeftButton
        self.pan = MouseConfig(*pan)
        self.rotate = MouseConfig(*rotate)
        self.drag_selection = MouseConfig(*drag_selection)
        self.drag_deselection = MouseConfig(*drag_deselection)
        self.multiselect = MouseConfig(*multiselect)
        self.deselect = MouseConfig(*deselect)
        self.actions = {k: ActionConfig(*v) for k, v in actions.items()}

    @classmethod
    def from_default(cls) -> "ControllerConfig":
        controller_config = ControllerConfig.from_json(Path(HERE, "configurations", "default_config", "controller.json"))
        if not isinstance(controller_config, ControllerConfig):
            raise TypeError(f"The {controller_config} is not a valid controller configuration file.")
        return controller_config

    @classmethod
    def from_json(cls, filepath) -> "ControllerConfig":
        controller_config = super().from_json(filepath)
        if not isinstance(controller_config, ControllerConfig):
            raise TypeError(f"The {filepath} is not a valid controller configuration file.")
        return controller_config
