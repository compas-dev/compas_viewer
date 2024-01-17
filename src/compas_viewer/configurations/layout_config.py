from pathlib import Path
from typing import Dict
from typing import List
from typing import Literal
from typing import TypedDict

from compas_viewer import DATA
from compas_viewer.configurations import Config


class StatusbarConfigType(TypedDict):
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


class MenubarConfigType(TypedDict):
    """
    The type template for each single item of the menu.
    """

    action: Literal["action", "link"]
    kwargs: List[str]


class ViewportConfigType(TypedDict):
    """
    The type template for each single item of the viewport.
    """

    category: Literal["render"]
    config_path: str


class ToolbarConfigType(TypedDict):
    """
    The type template for the each toolbar element.
    """

    action: str
    kwargs: dict


class ToolbarConfig(Config):
    """
    The class representation for the toolbar configuration of the Layout class.
    The toolbar configuration contains all the settings about the toolbar itself.
    """

    def __init__(self, config: Dict[str, Dict[str, ToolbarConfigType]]):
        super().__init__(config)

    @classmethod
    def from_json(cls, filepath) -> "ToolbarConfig":
        toolbar_config = super().from_json(filepath)
        if not isinstance(toolbar_config, ToolbarConfig):
            raise TypeError(f"The {filepath} is not a valid toolbar configuration file.")
        return toolbar_config


class ViewportConfig(Config):
    """
    The class representation for the viewport configuration of the Layout class.
    The viewport configuration contains all the settings about the viewport itself: render, ...

    Parameters
    ----------
    config : :class:`~ViewportConfigType`
        A TypedDict with defined keys and types.
    """

    def __init__(self, config: Dict[str, Dict[str, ViewportConfigType]]):
        super().__init__(config)

    @classmethod
    def from_json(cls, filepath) -> "ViewportConfig":
        viewport_config = super().from_json(filepath)
        if not isinstance(viewport_config, ViewportConfig):
            raise TypeError(f"The {filepath} is not a valid viewport configuration file.")
        return viewport_config


class MenubarConfig(Config):
    """
    The class representation for the menu bar configuration of the Layout class.
    The menu bar configuration contains all the settings about the menu bar itself: items, ...

    Parameters
    ----------
    config : :class:`~MenubarConfigType`
        A TypedDict with defined keys and types.
    """

    def __init__(self, config: Dict[str, Dict[str, MenubarConfigType]]):
        super().__init__(config)

    @classmethod
    def from_json(cls, filepath) -> "MenubarConfig":
        menu_config = super().from_json(filepath)
        if not isinstance(menu_config, MenubarConfig):
            raise TypeError(f"The {filepath} is not a valid menu configuration file.")
        return menu_config


class StatusbarConfig(Config):
    """
    The class representation for the status bar configuration of the Layout class.
    The status bar configuration contains all the settings about the status bar itself: text, show_fps, ...

    Parameters
    ----------
    config : :class:`~StatusbarConfigType`
        A TypedDict with defined keys and types.
    """

    def __init__(self, config: StatusbarConfigType):
        super().__init__(config)
        self.text = config["text"]
        self.show_fps = config["show_fps"]

    @classmethod
    def from_json(cls, filepath) -> "StatusbarConfig":
        statusbar_config = super().from_json(filepath)
        if not isinstance(statusbar_config, StatusbarConfig):
            raise TypeError(f"The {filepath} is not a valid statusbar configuration file.")
        return statusbar_config


class WindowConfig(Config):
    """
    The class representation for the window configuration of the Layout class.
    The window configuration contains all the settings about the window itself: width, height, fullscreen, ...

    Parameters
    ----------
    config : :class:`~WindowConfigType`
        A TypedDict with defined keys and types.
    """

    def __init__(self, config: WindowConfigType):
        super().__init__(config)
        self.about = config["about"]
        self.title = config["title"]
        self.width = config["width"]
        self.height = config["height"]
        self.fullscreen = config["fullscreen"]

    @classmethod
    def from_json(cls, filepath) -> "WindowConfig":
        window_config = super().from_json(filepath)
        if not isinstance(window_config, WindowConfig):
            raise TypeError(f"The {filepath} is not a valid window configuration file.")
        return window_config


class LayoutConfigType(TypedDict):
    """
    The type template for the layout.json file.
    """

    window: WindowConfig
    statusbar: StatusbarConfig
    menubar: MenubarConfig
    viewport: ViewportConfig
    toolbar: ToolbarConfig


class LayoutConfig(Config):
    """
    The class representation for the `layout.json` of the Layout class.
    The layout.json contains all the settings about the viewer application it self: width, height, fullscreen, ...

    Parameters
    ----------
    config : :class:`~LayoutConfigType`
        A TypedDict with defined keys and types.
    """

    def __init__(self, config: LayoutConfigType):
        super().__init__(config)
        self.window = config["window"]
        self.statusbar = config["statusbar"]
        self.menubar = config["menubar"]
        self.viewport = config["viewport"]
        self.toolbar = config["toolbar"]

    @classmethod
    def from_default(cls) -> "LayoutConfig":
        """
        Load the default configuration.
        """
        layout_config = LayoutConfig.from_json(Path(DATA, "default_config", "layout.json"))
        if not isinstance(layout_config, LayoutConfig):
            raise TypeError(f"The default layout.json is not a valid layout configuration file.")
        return layout_config

    @classmethod
    def from_json(cls, filepath) -> "LayoutConfig":
        layout_config = super().from_json(filepath)
        if not isinstance(layout_config, LayoutConfig):
            raise TypeError(f"The {filepath} is not a valid layout configuration file.")
        return layout_config
