import json
from dataclasses import dataclass
from dataclasses import field
from typing import Literal

from compas.colors import Color


@dataclass
class CameraConfig:
    position: list[float]
    target: list[float] = field(default_factory=lambda: [0, 0, 0])
    up: list[float] = field(default_factory=lambda: [0, 0, 1])
    near: float = 0.1
    far: float = 1000
    fov: float = 50


@dataclass
class View3dConfig:
    viewport: Literal["top", "perspective"] = "perspective"
    background: Color = field(default_factory=lambda: Color.from_hex("#eeeeee"))
    width: float = 1100
    height: float = 580
    show_grid: bool = True
    show_axes: bool = True

    camera: CameraConfig = field(init=False)

    def __post_init__(self):
        position = [0, -10, 5] if self.viewport == "perspective" else [0, 0, 1]
        self.camera = CameraConfig(position=position)


@dataclass
class SidebarConfig:
    show: bool = True
    items: list[dict[str, str]] = None

@dataclass
class ToolbarConfig:
    show: bool = True
    items: list[dict[str, str]] = None

@dataclass
class MenubarConfig:
    show: bool = True
    items: list[dict[str, str]] = None

@dataclass
class StatusbarConfig:
    show: bool = True
    items: list[dict[str, str]] = None

@dataclass
class UIConfig:
    menubar: bool = True
    toolbar: bool = True
    statusbar: bool = True
    sidebar: SidebarConfig = field(default_factory=SidebarConfig)
    view3d: View3dConfig = field(default_factory=View3dConfig)

@dataclass
class Config:

    ui = UIConfig()

    @classmethod
    def from_json(cls, filepath):
        with open(filepath) as fp:
            data: dict = json.load(fp)
        config = cls()
        if "ui" in data:
            if "sidebar" in data["ui"]:
                config.ui.sidebar.show = data["ui"]["sidebar"].get("show")
                config.ui.sidebar.items = data["ui"]["sidebar"].get("items")
        return config