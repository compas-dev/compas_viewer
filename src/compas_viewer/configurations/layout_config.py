from pathlib import Path
from typing import Literal
from typing import TypedDict

from compas_viewer import HERE

from .config import Config


class ToolbarConfig(Config):
    """
    The class representation for the toolbar configuration of the Layout class.
    The toolbar configuration contains all the settings about the toolbar itself.

    Parameters
    ----------
    config : dict[str, dict[str, :class:`compas_viewer.configurations.layout_config.ToolbarConfigType`]]
        A TypedDict with defined keys and types.

    Attributes
    ----------
    ToolbarConfigType : :class:`compas_viewer.configurations.layout_config.ToolbarConfigType`
        The type template for the each toolbar element: {action: str, kwargs: dict}

    See Also
    --------
    :class:`compas_viewer.configurations.layout_config.ToolbarConfigType`
    :class:`compas_viewer.layout.toolbar.ToolbarLayout`
    :class:`compas_viewer.configurations.layout_config.LayoutConfig`
    """

    class ToolbarConfigType(TypedDict):
        """
        The type template for the each toolbar element.
        """

        action: str
        kwargs: dict

    def __init__(self, config: dict[str, dict[str, ToolbarConfigType]]):
        super().__init__()
        self.config = config

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
    config : dict[str, dict[str, :class:`compas_viewer.configurations.layout_config.ViewportConfigType`]]
        A TypedDict with defined keys and types.

    Attributes
    ----------
    ViewportConfigType : :class:`compas_viewer.configurations.layout_config.ViewportConfigType`
        The type template for each single item of the viewport: {category: str, config_path: str}

    See Also
    --------
    :class:`compas_viewer.configurations.layout_config.ViewportConfigType`
    :class:`compas_viewer.layout.viewport.ViewportLayout`
    :class:`compas_viewer.configurations.layout_config.LayoutConfig`
    """

    class ViewportConfigType(TypedDict):
        """
        The type template for each single item of the viewport.
        """

        category: Literal["render"]
        config_path: str

    def __init__(self, config: dict[str, dict[str, ViewportConfigType]]):
        super().__init__()
        self.config = config

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
    config : dict[str, dict[str, :class:`compas_viewer.configurations.layout_config.MenubarConfigType`]]
        A TypedDict with defined keys and types.

    Attributes
    ----------
    MenubarConfigType : :class:`compas_viewer.configurations.layout_config.MenubarConfigType`
        The type template for each single item of the menu: {action: str, kwargs: list[str]}

    See Also
    --------
    :class:`compas_viewer.configurations.layout_config.MenubarConfigType`
    :class:`compas_viewer.layout.menubar.MenubarLayout`
    :class:`compas_viewer.configurations.layout_config.LayoutConfig`
    """

    class MenubarConfigType(TypedDict):
        """
        The type template for each single item of the menu.
        """

        action: Literal["action", "link"]
        kwargs: list[str]

    def __init__(self, config: dict[str, dict[str, MenubarConfigType]]):
        super().__init__()
        self.config = config

    @classmethod
    def from_json(cls, filepath) -> "MenubarConfig":
        menubar_config = super().from_json(filepath)
        if not isinstance(menubar_config, MenubarConfig):
            raise TypeError(f"The {filepath} is not a valid menubar configuration file.")
        return menubar_config


class StatusbarConfig(Config):
    """
    The class representation for the status bar configuration of the Layout class.
    The status bar configuration contains all the settings about the status bar itself: text, show_fps, ...

    Parameters
    ----------
    text : str
        The text of the status bar.
    show_fps : bool
        Whether to show the fps or not.

    See Also
    --------
    :class:`compas_viewer.layout.statusbar.StatusbarLayout`
    :class:`compas_viewer.configurations.layout_config.LayoutConfig`
    """

    def __init__(self, text: str, show_fps: bool):
        super().__init__()
        self.text = text
        self.show_fps = show_fps

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
    about : str
        The about text of the window.
    title : str
        The title of the window.
    width : int
        The width of the window.
    height : int
        The height of the window.
    fullscreen : bool
        Whether to show the window in fullscreen or not.

    See Also
    --------
    :class:`compas_viewer.layout.window.WindowLayout`
    :class:`compas_viewer.configurations.layout_config.LayoutConfig`
    """

    def __init__(self, about: str, title: str, width: int, height: int, fullscreen: bool):
        super().__init__()
        self.about = about
        self.title = title
        self.width = width
        self.height = height
        self.fullscreen = fullscreen

    @classmethod
    def from_json(cls, filepath) -> "WindowConfig":
        window_config = super().from_json(filepath)
        if not isinstance(window_config, WindowConfig):
            raise TypeError(f"The {filepath} is not a valid window configuration file.")
        return window_config


class LayoutConfig(Config):
    """
    The class representation for the `layout.json` of the Layout class.
    The layout.json contains all the settings about the viewer application it self: width, height, fullscreen, ...

    Parameters
    ----------
    window : :class:`compas_viewer.configurations.layout_config.WindowConfig`
        The window configuration.
    statusbar : :class:`compas_viewer.configurations.layout_config.StatusbarConfig`
        The status bar configuration.
    menubar : :class:`compas_viewer.configurations.layout_config.MenubarConfig`
        The menu bar configuration.
    viewport : :class:`compas_viewer.configurations.layout_config.ViewportConfig`
        The viewport configuration.
    toolbar : :class:`compas_viewer.configurations.layout_config.ToolbarConfig`
        The toolbar configuration.

    See Also
    --------
    :class:`compas_viewer.configurations.layout_config.WindowConfig`
    :class:`compas_viewer.configurations.layout_config.StatusbarConfig`
    :class:`compas_viewer.configurations.layout_config.MenubarConfig`
    :class:`compas_viewer.configurations.layout_config.ViewportConfig`
    :class:`compas_viewer.configurations.layout_config.ToolbarConfig`
    :class:`compas_viewer.layout.Layout`
    """

    def __init__(
        self,
        window: WindowConfig,
        statusbar: StatusbarConfig,
        menubar: MenubarConfig,
        viewport: ViewportConfig,
        toolbar: ToolbarConfig,
    ):
        super().__init__()
        self.window = window
        self.statusbar = statusbar
        self.menubar = menubar
        self.viewport = viewport
        self.toolbar = toolbar

    @classmethod
    def from_default(cls) -> "LayoutConfig":
        """
        Load the default configuration.
        """
        layout_config = LayoutConfig.from_json(Path(HERE, "configurations", "default_config", "layout.json"))
        if not isinstance(layout_config, LayoutConfig):
            raise TypeError(f"The {layout_config} is not a valid layout configuration file.")
        return layout_config

    @classmethod
    def from_json(cls, filepath) -> "LayoutConfig":
        layout_config = super().from_json(filepath)
        if not isinstance(layout_config, LayoutConfig):
            raise TypeError(f"The {filepath} is not a valid layout configuration file.")
        return layout_config
