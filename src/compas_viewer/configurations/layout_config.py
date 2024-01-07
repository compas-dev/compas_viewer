from pathlib import Path
from typing import TypedDict

from compas_viewer import DATA
from compas_viewer.configurations import Config


class StatusBarConfigType(TypedDict):
    """
    The type template for the status bar only.
    """

    text: str
    show_fps: bool


class WindowConfigType(TypedDict):
    """
    The type template for the main window only.
    """

    about: str
    title: str
    width: int
    height: int
    fullscreen: bool


class LayoutConfigType(TypedDict):
    """
    The type template for the layout.json file.
    """

    window: WindowConfigType
    statusbar: StatusBarConfigType


class LayoutConfig(Config):
    """
    The class representation for the `layout.json` of the class :class:`compas_viewer.layout.Layout`
    The layout.json contains all the settings about the viewer application it self: width, height, fullscreen, ...

    Parameters
    ----------
    config : :class:`LayoutConfigType`
        A TypedDict with defined keys and types.

    References
    ----------
    * https://doc.qt.io/qt-6/designer-using-a-ui-file.html

    """

    def __init__(self, config: LayoutConfigType):
        super().__init__(config)
        self.window = config["window"]
        self.statusbar = config["statusbar"]

    @classmethod
    def from_default(cls) -> "LayoutConfig":
        """
        Load the default configuration.
        """
        layout_config = LayoutConfig.from_json(Path(DATA, "default_config", "layout.json"))
        assert isinstance(layout_config, LayoutConfig)
        return layout_config

    @classmethod
    def from_json(cls, filepath) -> "LayoutConfig":
        layout_config = super().from_json(filepath)
        assert isinstance(layout_config, LayoutConfig)
        return layout_config
