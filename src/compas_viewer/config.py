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
    camera: CameraConfig = field(default_factory=CameraConfig)


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
class SidebarConfig:
    show: bool = False
    items: list[dict[str, str]] = None


@dataclass
class WindowConfig:
    title: str = "COMPAS Viewer"
    width: int = 1280
    height: int = 720
    fullscreen: bool = False
    about: str = "Stand-alone viewer for COMPAS."


@dataclass
class UIConfig:
    menubar: MenubarConfig = field(default_factory=MenubarConfig)
    toolbar: ToolbarConfig = field(default_factory=ToolbarConfig)
    statusbar: StatusbarConfig = field(default_factory=StatusbarConfig)
    sidebar: SidebarConfig = field(default_factory=SidebarConfig)
    view3d: View3dConfig = field(default_factory=View3dConfig)
    window: WindowConfig = field(default_factory=WindowConfig)


@dataclass
class Config:

    ui: UIConfig = field(default_factory=UIConfig)

    @classmethod
    def from_json(cls, filepath):
        with open(filepath) as fp:
            data: dict = json.load(fp)
        config = cls(**data)
        return config

    @classmethod
    def to_json(cls, config, filepath):
        data = config.__dict__
        with open(filepath, "w") as fp:
            json.dump(data, fp, indent=4)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    
    @classmethod
    def to_dict(cls, config):
        return config.__dict__