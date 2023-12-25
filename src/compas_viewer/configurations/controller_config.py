from pathlib import Path
from typing import Dict
from typing import List
from typing import Literal
from typing import TypedDict

from compas_viewer import DATA
from compas_viewer.configurations import Config


class SelectType(TypedDict):
    """
    The type template for the select only.
    """

    mouse: Literal["left", "right", "middle"]
    multiselect: str
    deselect: str


class MouseConfigType(TypedDict):
    """
    The type template for the mouse only.
    """

    zoom: Dict[str, str]
    pan: Dict[str, str]
    rotate: Dict[str, str]
    drag_selection: Dict[str, str]
    drag_deselection: Dict[str, str]
    select: SelectType


class KeyConfigType(TypedDict):
    """
    The type template for the key only.
    """

    name: str
    keys: List[str]


class ControllerConfigType(TypedDict):
    """
    The type template for the `controller.json`.
    """

    mouse: MouseConfigType
    keys: List[KeyConfigType]


class KeyConfig(Config):
    """
    The class representation for the key only.

    Parameters
    ----------
    config : :class:`KeyConfigType`
        A TypedDict with defined keys and types.
    """

    def __init__(self, config: KeyConfigType) -> None:
        super(KeyConfig, self).__init__(config)
        self.name = config["name"]
        self.keys = config["keys"]


class ControllerConfig(Config):
    """
    The class representation for the `controller.json` of the class :class:`compas_viewer.controller.Controller`
    The controller.json contains all the settings about controlling the viewer: mouse, keys, ...

    Parameters
    ----------
    config : :class:`ControllerConfigType`
        A TypedDict with defined keys and types.
    """

    def __init__(self, config: ControllerConfigType) -> None:
        super(ControllerConfig, self).__init__(config)
        self.pan = config["mouse"]["pan"]
        self.zoom = config["mouse"]["zoom"]
        self.rotate = config["mouse"]["rotate"]
        self.drag_selection = config["mouse"]["drag_selection"]
        self.drag_deselection = config["mouse"]["drag_deselection"]
        self.select: str = config["mouse"]["select"]["mouse"]
        self.multiselect: str = config["mouse"]["select"]["multiselect"]
        self.deselect: str = config["mouse"]["select"]["deselect"]
        for key in config["keys"]:
            setattr(self, key["name"], KeyConfig(key))

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
