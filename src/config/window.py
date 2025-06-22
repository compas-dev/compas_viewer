from .base import BaseConfig


class WindowConfig(BaseConfig):
    """Configuration for the main window."""
    
    title: str = "COMPAS Viewer"
    width: int = 1280
    height: int = 720
    fullscreen: bool = False
    about: str = "Stand-alone viewer for COMPAS." 