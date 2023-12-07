from pathlib import Path
from typing import TypedDict

from compas_viewer import DATA
from compas_viewer.configurations import Config


class ViewerConfigData(TypedDict):
    """
    The type template for the `viewer.json`.
    """

    about: str
    title: str
    width: int
    height: int
    full_screen: bool


class ViewerConfig(Config):
    """
    The class representation for the `viewer.json`.
    The viewer.json contains all the settings about the viewer application it self: with, height, full_screen, ...

    """

    def __init__(self, config: ViewerConfigData) -> None:
        super(ViewerConfig, self).__init__(config)
        self.about = config["about"]
        self.title = config["title"]
        self.width = config["width"]
        self.height = config["height"]
        self.full_screen = config["full_screen"]

    @classmethod
    def from_default(cls):
        """
        Load the default configuration.
        """
        return Config.from_json(Path(DATA, "default_config", "viewer.json"))
