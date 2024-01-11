from pathlib import Path
from typing import Dict
from typing import List
from typing import Literal
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


class MenuBarConfigType(TypedDict):
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


class ToolBarConfigType(TypedDict):
    """
    The type template for the each toolbar element.
    """

    action: str
    kwargs: dict


class ToolBarConfig(Config):
    """
    The class representation for the toolbar configuration of the class :class:`compas_viewer.layout.ToolBarLayout`.
    The toolbar configuration contains all the settings about the toolbar itself.
    """

    def __init__(self, config: Dict[str, Dict[str, ToolBarConfigType]]):
        super().__init__(config)

    @classmethod
    def from_json(cls, filepath) -> "ToolBarConfig":
        toolbar_config = super().from_json(filepath)
        assert isinstance(toolbar_config, ToolBarConfig)
        return toolbar_config


class ViewportConfig(Config):
    """
    The class representation for the menu bar configuration of the class :class:`compas_viewer.layout.ViewportLayout`.
    The viewport configuration contains all the settings about the viewport itself: render, ...
    """

    def __init__(self, config: Dict[str, Dict[str, ViewportConfigType]]):
        super().__init__(config)

    @classmethod
    def from_json(cls, filepath) -> "ViewportConfig":
        viewport_config = super().from_json(filepath)
        assert isinstance(viewport_config, ViewportConfig)
        return viewport_config


class MenuBarConfig(Config):
    """
    The class representation for the menu bar configuration of the class :class:`compas_viewer.layout.Layout`.
    The menu bar configuration contains all the settings about the menu bar itself: items, ...
    """

    def __init__(self, config: Dict[str, Dict[str, MenuBarConfigType]]):
        super().__init__(config)

    @classmethod
    def from_json(cls, filepath) -> "MenuBarConfig":
        menu_config = super().from_json(filepath)
        assert isinstance(menu_config, MenuBarConfig)
        return menu_config


class StatusBarConfig(Config):
    """
    The class representation for the status bar configuration of the class :class:`compas_viewer.layout.Layout`.
    The status bar configuration contains all the settings about the status bar itself: text, show_fps, ...

    Parameters
    ----------
    config : :class:`StatusBarConfigType`
        A TypedDict with defined keys and types.
    """

    def __init__(self, config: StatusBarConfigType):
        super().__init__(config)
        self.text = config["text"]
        self.show_fps = config["show_fps"]

    @classmethod
    def from_json(cls, filepath) -> "StatusBarConfig":
        statusbar_config = super().from_json(filepath)
        assert isinstance(statusbar_config, StatusBarConfig)
        return statusbar_config


class WindowConfig(Config):
    """
    The class representation for the window configuration of the class :class:`compas_viewer.layout.Layout`.
    The window configuration contains all the settings about the window itself: width, height, fullscreen, ...

    Parameters
    ----------
    config : :class:`WindowConfigType`
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
        assert isinstance(window_config, WindowConfig)
        return window_config


class LayoutConfigType(TypedDict):
    """
    The type template for the layout.json file.
    """

    window: WindowConfig
    statusbar: StatusBarConfig
    menubar: MenuBarConfig
    viewport: ViewportConfig
    toolbar: ToolBarConfig


class LayoutConfig(Config):
    """
    The class representation for the `layout.json` of the class :class:`compas_viewer.layout.Layout`
    The layout.json contains all the settings about the viewer application it self: width, height, fullscreen, ...

    Parameters
    ----------
    config : :class:`LayoutConfigType`
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
        assert isinstance(layout_config, LayoutConfig)
        return layout_config

    @classmethod
    def from_json(cls, filepath) -> "LayoutConfig":
        layout_config = super().from_json(filepath)
        assert isinstance(layout_config, LayoutConfig)
        return layout_config
