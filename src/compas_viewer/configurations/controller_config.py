from pathlib import Path
from typing import Dict
from typing import TypedDict

from PySide6.QtCore import Qt

from compas_viewer import DATA
from compas_viewer.configurations import Config
from compas_viewer.utilities import key_mapper


class MouseConfigType(TypedDict):
    """
    The type template for the mouse-based movement only.
    """

    mouse: str
    modifier: str


class ActionConfigType(TypedDict):
    """
    The type template for the key-based actions only.
    """

    key: str
    modifier: str


class ControllerConfigType(TypedDict):
    """
    The type template for the `controller.json`
    which contains mouse-based movement and key-based actions.
    """

    pan: MouseConfigType
    rotate: MouseConfigType
    drag_selection: MouseConfigType
    drag_deselection: MouseConfigType
    multiselect: MouseConfigType
    deselect: MouseConfigType
    actions: Dict[str, ActionConfigType]


class ActionConfig:
    """
    The class representation  of the key-based action configuration.
    The action config contains two elements, "key" and "modifier".

    Parameters
    ----------
    config : :class:`ActionConfigType`
        A TypedDict with defined keys and types.

    Attributes
    ----------
    config : :class:`ActionConfigType`
        A TypedDict with defined keys and types.
    key : :class:`PySide6.QtCore.Qt.Key`
        The Qt key.
    modifier : :class:`PySide6.QtCore.Qt.KeyboardModifier`
        The Qt modifier.
    """

    def __init__(self, config: ActionConfigType):
        self.config = config
        self.key = key_mapper(config["key"], 0)
        self.modifier = key_mapper(config["modifier"], 1)


class MouseConfig:
    """
    The class representation of the mouse-based movement configuration.
    The mouse contains two elements, "mouse" and "modifier".

    Parameters
    ----------
    config : :class:`MouseConfigType`
        A TypedDict with defined keys and types.

    Attributes
    ----------
    config : :class:`MouseConfigType`
        A TypedDict with defined keys and types.
    mouse : :class:`PySide6.QtCore.Qt.MouseButton`
        The Qt mouse.
    modifier : :class:`PySide6.QtCore.Qt.KeyboardModifier`
        The Qt modifier.
    """

    def __init__(self, config: MouseConfigType):
        self.config = config
        self.mouse = key_mapper(config["mouse"], 2)
        self.modifier = key_mapper(config["modifier"], 1)


class ControllerConfig(Config):
    """
    The class representation for the `controller.json` of
    the class :class:`compas_viewer.controller.controller.Controller`
    The controller.json contains all the settings about controlling the viewer: mouse, keys, ...

    Parameters
    ----------
    config : :class:`ControllerConfigType`
        A TypedDict with defined keys and types.
    """

    def __init__(self, config: ControllerConfigType) :
        super(ControllerConfig, self).__init__(config)
        # Zoom function fixed.
        self.zoom = None
        # Select function fixed.
        self.select = Qt.MouseButton.LeftButton
        self.pan = MouseConfig(config["pan"])
        self.rotate = MouseConfig(config["rotate"])
        self.drag_selection = MouseConfig(config["drag_selection"])
        self.drag_deselection = MouseConfig(config["drag_deselection"])
        self.multiselect = MouseConfig(config["multiselect"])
        self.deselect = MouseConfig(config["deselect"])
        self.actions = {k: ActionConfig(v) for k, v in config["actions"].items()}

    @classmethod
    def from_default(cls) -> "ControllerConfig":
        controller_config = ControllerConfig.from_json(Path(DATA, "default_config", "controller.json"))
        assert isinstance(controller_config, ControllerConfig)
        return controller_config

    @classmethod
    def from_json(cls, filepath) -> "ControllerConfig":
        controller_config = super().from_json(filepath)
        assert isinstance(controller_config, ControllerConfig)
        return controller_config
