from .base import BaseConfig
from .renderer import DisplayConfig, View3DConfig


class ToolbarConfig(BaseConfig):
    """Configuration for the toolbar."""
    
    show: bool = False


class MenubarConfig(BaseConfig):
    """Configuration for the menubar."""
    
    show: bool = True


class StatusbarConfig(BaseConfig):
    """Configuration for the status bar."""
    
    show: bool = True


class SidebarConfig(BaseConfig):
    """Configuration for the sidebar."""
    
    show: bool = True
    show_widgets: bool = True
    sceneform_visible: bool = True
    objectsetting_visible: bool = True


class SideDockConfig(BaseConfig):
    """Configuration for the side dock."""
    
    show: bool = False


class UIConfig(BaseConfig):
    """Configuration for the user interface."""
    
    menubar: MenubarConfig = MenubarConfig()
    toolbar: ToolbarConfig = ToolbarConfig()
    statusbar: StatusbarConfig = StatusbarConfig()
    sidebar: SidebarConfig = SidebarConfig()
    sidedock: SideDockConfig = SideDockConfig()
    view3d: View3DConfig = View3DConfig()
    display: DisplayConfig = DisplayConfig() 