from typing import Literal, List, Tuple

from .base import BaseConfig


class DisplayConfig(BaseConfig):
    """Configuration for display settings."""
    
    pointcolor: str = "#000000"  # Color as hex string instead of Color object
    linecolor: str = "#000000"
    surfacecolor: str = "#808080"
    pointsize: float = 6.0
    linewidth: float = 1.0
    opacity: float = 1.0


class RendererConfig(BaseConfig):
    """Configuration for the renderer."""
    
    show_grid: bool = True
    show_gridz: bool = False
    gridmode: Literal["full", "quadrant"] = "full"
    gridsize: Tuple[float, int, float, int] = (10.0, 10, 10.0, 10)
    gridcolor: str = "#b3b3b3"  # Color as hex string
    opacity: float = 1.0
    ghostopacity: float = 0.7
    rendermode: Literal["ghosted", "shaded", "lighted", "wireframe"] = "shaded"
    view: Literal["perspective", "front", "right", "top"] = "perspective"
    backgroundcolor: str = "#ffffff"  # Color as hex string
    selectioncolor: str = "#ffff00"  # Color as hex string


class CameraConfig(BaseConfig):
    """Configuration for the camera."""
    
    fov: float = 45.0
    near: float = 0.1
    far: float = 1000.0
    position: List[float] = [-10.0, -10.0, 10.0]
    target: List[float] = [0.0, 0.0, 0.0]
    scale: float = 1.0
    zoomdelta: float = 0.05
    rotationdelta: float = 0.01
    pandelta: float = 0.05


class View3DConfig(BaseConfig):
    """Configuration for the 3D view."""
    
    viewport: Literal["top", "perspective"] = "perspective"
    background: str = "#eeeeee"  # Color as hex string 