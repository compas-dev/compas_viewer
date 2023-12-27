from pathlib import Path
from typing import TypedDict

from compas_viewer import DATA
from compas_viewer.configurations import Config


class ViewerConfigType(TypedDict):
    """
    The type template for the `viewer.json`.
    """

    about: str
    title: str
    width: int
    height: int
    fullscreen: bool
    statusbar: str
    show_fps: bool


class ViewerConfig(Config):
    """
    The class representation for the `viewer.json` of the class :class:`compas_viewer.viewer.Viewer`
    The viewer.json contains all the settings about the viewer application it self: width, height, fullscreen, ...

    Parameters
    ----------
    config : :class:`ViewerConfigType`
        A TypedDict with defined keys and types.

    """

    def __init__(self, config: ViewerConfigType) -> None:
        super().__init__(config)
        self.about = config["about"]
        self.title = config["title"]
        self.width = config["width"]
        self.height = config["height"]
        self.fullscreen = config["fullscreen"]
        self.statusbar = config["statusbar"]
        self.show_fps = config["show_fps"]

    @classmethod
    def from_default(cls) -> "ViewerConfig":
        """
        Load the default configuration.
        """
        viewer_config = ViewerConfig.from_json(Path(DATA, "default_config", "viewer.json"))
        assert isinstance(viewer_config, ViewerConfig)
        return viewer_config

    @classmethod
    def from_json(cls, filepath) -> "ViewerConfig":
        viewer_config = super().from_json(filepath)
        assert isinstance(viewer_config, ViewerConfig)
        return viewer_config
