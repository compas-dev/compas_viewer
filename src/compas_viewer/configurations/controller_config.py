from pathlib import Path
from typing import Dict
from typing import List
from typing import TypedDict

from compas_viewer import DATA
from compas_viewer.configurations import Config


class MouseConfigData(TypedDict):
    """
    The type template for the mouse only.
    """

    zoom: Dict[str, str]
    pan: Dict[str, str]
    rotate: Dict[str, str]
    box_selection: Dict[str, str]
    box_deselection: Dict[str, str]
    selection: Dict[str, str]


class KeyConfigData(TypedDict):
    """
    The type template for the key only.
    """

    name: str
    keys: List[str]


class ControllerConfigData(TypedDict):
    """
    The type template for the `controller.json`.
    """

    mouse: MouseConfigData
    keys: List[KeyConfigData]


class KeyConfig(Config):
    """
    The class representation for the key only.

    Parameters
    ----------------
    config : KeyConfigData
        A TypedDict with defined keys and types.
    """

    def __init__(self, config: KeyConfigData) -> None:
        super(KeyConfig, self).__init__(config)
        self.name = config["name"]
        self.keys = config["keys"]


class ControllerConfig(Config):
    """
    The class representation for the `controller.json`.
    The controller.json contains all the settings about controlling the viewer: mouse, keys, ...

    Parameters
    ----------------
    config : ControllerConfigData
        A TypedDict with the following keys:
            mouse: MouseConfigData
            keys: List[KeyConfigData]

    """

    def __init__(self, config: ControllerConfigData) -> None:
        super(ControllerConfig, self).__init__(config)
        self.pan = config["mouse"]["pan"]
        self.zoom = config["mouse"]["zoom"]
        self.rotate = config["mouse"]["rotate"]
        self.box_selection = config["mouse"]["box_selection"]
        self.selection: str = config["mouse"]["selection"]["mouse"]
        self.multi_selection: str = config["mouse"]["selection"]["multi_selection"]
        self.deletion: str = config["mouse"]["selection"]["deselection"]
        for key in config["keys"]:
            setattr(self, key["name"], KeyConfig(key))

    @classmethod
    def from_default(cls):
        """
        Load the default configuration.
        """
        return ControllerConfig.from_json(Path(DATA, "default_config", "controller.json"))
