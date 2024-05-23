import json
from dataclasses import dataclass
from dataclasses import field
from dataclasses import is_dataclass
from functools import partial
from typing import Literal

from compas.colors import Color
from compas_viewer.actions import change_viewmode
from compas_viewer.actions import open_camera_settings_dialog
from compas_viewer.actions import pan_view
from compas_viewer.actions import rotate_view
from compas_viewer.actions import select_all
from compas_viewer.actions import select_object
from compas_viewer.actions import select_window
from compas_viewer.actions import zoom_selected
from compas_viewer.actions import zoom_view


class ConfigBase:
    @classmethod
    def from_json(cls, filepath):
        with open(filepath) as fp:
            data: dict = json.load(fp)
        config = cls(**data)
        return config

    def to_json(self, filepath):
        with open(filepath, "w") as fp:
            json.dump(self.to_dict(), fp, indent=4)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        data = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                data[key] = value.to_dict() if hasattr(value, "to_dict") else value
        return data

    def __post_init__(self):
        for field_name, field_value in self.__dict__.items():
            field_type = self.__annotations__[field_name]
            if isinstance(field_value, dict) and is_dataclass(field_type):
                # Convert dict to dataclass if the field type is a dataclass
                setattr(self, field_name, field_type(**field_value))
            elif isinstance(field_value, dict) and not is_dataclass(field_type):
                raise ValueError(f"Expected dataclass type for field '{field_name}' but got dict.")


# this should be part of View3D config
@dataclass
class DisplayConfig(ConfigBase):
    pointcolor: Color = field(default_factory=Color.black)
    linecolor: Color = field(default_factory=Color.black)
    surfacecolor: Color = field(default_factory=Color.grey)
    pointsize: float = float(6.0)
    linewidth: float = float(1.0)
    opacity: float = float(1.0)


@dataclass
class View3dConfig(ConfigBase):
    viewport: Literal["top", "perspective"] = "perspective"
    background: Color = field(default_factory=lambda: Color.from_hex("#eeeeee"))


@dataclass
class ToolbarConfig(ConfigBase):
    show: bool = False
    items: list[dict] = field(default_factory=lambda: [])


@dataclass
class MenubarConfig(ConfigBase):
    show: bool = True
    items: list[dict] = field(
        default_factory=lambda: [
            {
                "title": "View",
                "items": [
                    {"title": "Shaded", "action": lambda: print("Shaded")},
                    {"title": "Ghosted", "action": lambda: print("Ghosted")},
                    {"title": "Lighted", "action": lambda: print("Lighted")},
                    {"title": "Wireframe", "action": lambda: print("Wireframe")},
                    {"type": "separator"},
                    {"title": "Perspective", "action": partial(change_viewmode, "perspective")},
                    {"title": "Top", "action": partial(change_viewmode, "top")},
                    {"title": "Front", "action": partial(change_viewmode, "front")},
                    {"title": "Right", "action": partial(change_viewmode, "right")},
                    {"type": "separator"},
                    {"title": "Camera Settings", "action": open_camera_settings_dialog},
                    {"type": "separator"},
                ],
            },
            {
                "title": "Display",
                "items": [],
            },
            {
                "title": "Scene",
                "items": [
                    {"title": "Clear Scene", "action": lambda: print("Clear scene")},
                    {"type": "separator"},
                    {"title": "Load Scene", "action": lambda: print("Load scene")},
                    {"title": "Save Scene", "action": lambda: print("Save scene")},
                ],
            },
            {
                "title": "Data",
                "items": [
                    {"title": "From JSON", "action": lambda: print("From JSON")},
                    {"type": "separator"},
                    {
                        "title": "Geometry",
                        "items": [
                            {"title": "Geometry From OBJ", "action": lambda: print("From OBJ")},
                            {"title": "Geometry From OFF", "action": lambda: print("From OFF")},
                            {"title": "Geometry From STP", "action": lambda: print("From STP")},
                            {"title": "Geometry From STL", "action": lambda: print("From STL")},
                        ],
                    },
                    {
                        "title": "Pointcloud",
                        "items": [],
                    },
                ],
            },
            {
                "title": "Server",
                "items": [
                    {"title": "Start Server", "action": lambda: print("Start Server")},
                    {"title": "Stop Server", "action": lambda: print("Stop Server")},
                    {"type": "separator"},
                    {"title": "Restart Server", "action": lambda: print("Restart Server")},
                    {"title": "Ping Server", "action": lambda: print("Ping Server")},
                ],
            },
            {
                "title": "Help",
                "items": [
                    {"title": "Viewer Docs", "action": lambda: print("Viewer docs")},
                    {"title": "Viewer Tutorials", "action": lambda: print("Viewer tutorials")},
                    {"title": "Viewer Examples", "action": lambda: print("Viewer examples")},
                    {"title": "Viewer Configs", "action": lambda: print("Viewer configs")},
                    {"type": "separator"},
                    {"title": "COMPAS Tutorials", "action": lambda: print("COMPAS Tutorials")},
                    {"title": "COMPAS Reference", "action": lambda: print("COMPAS Reference")},
                ],
            },
        ]
    )


@dataclass
class StatusbarConfig(ConfigBase):
    show: bool = True
    items: list[dict[str, str]] = None


@dataclass
class SidebarConfig(ConfigBase):
    show: bool = True
    items: list[dict[str, str]] = None


@dataclass
class WindowConfig(ConfigBase):
    title: str = "COMPAS Viewer"
    width: int = 1280
    height: int = 720
    fullscreen: bool = False
    about: str = "Stand-alone viewer for COMPAS."


@dataclass
class UIConfig(ConfigBase):
    menubar: MenubarConfig = field(default_factory=MenubarConfig)
    toolbar: ToolbarConfig = field(default_factory=ToolbarConfig)
    statusbar: StatusbarConfig = field(default_factory=StatusbarConfig)
    sidebar: SidebarConfig = field(default_factory=SidebarConfig)
    view3d: View3dConfig = field(default_factory=View3dConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)


# this should be part of View3D config
@dataclass
class RendererConfig(ConfigBase):
    show_grid: bool = True
    show_gridz: bool = False
    gridsize: tuple[float, int, float, int] = field(default_factory=lambda: (10.0, 10, 10.0, 10))
    opacity: float = 1.0
    ghostopacity: float = 0.7
    rendermode: Literal["ghosted", "shaded", "lighted", "wireframe"] = "shaded"
    viewmode: Literal["perspective", "front", "right", "top"] = "perspective"
    backgroundcolor: Color = field(default_factory=Color.white)


# this should be part of View3D config
@dataclass
class CameraConfig(ConfigBase):
    fov: float = 45.0
    near: float = 0.1
    far: float = 1000.0
    position: list[float] = field(default_factory=lambda: [0.0, -10.0, 10.0])
    target: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    scale: float = 1.0
    zoomdelta: float = 0.05
    rotationdelta: float = 0.01
    pandelta: float = 0.05


# this should not be exposed
@dataclass
class SelectorConfig(ConfigBase):
    enable: bool = True
    selectioncolor: Color = field(default_factory=lambda: Color(1.0, 1.0, 0.0, 1.0))


@dataclass
class KeyEvents:
    items: list[dict] = field(
        default_factory=lambda: [
            {"title": "Zoom Selected", "key": "F", "modifier": None, "action": zoom_selected},
            {"title": "Select All", "key": "A", "modifier": "CTRL", "action": select_all},
        ]
    )


@dataclass
class MouseEvents:
    items: list[dict] = field(
        default_factory=lambda: [
            {"title": "Pan View", "button": "RIGHT", "modifier": "SHIFT", "action": pan_view},
            {"title": "Rotate View", "button": "RIGHT", "modifier": None, "action": rotate_view},
            {"title": "Select", "button": "LEFT", "modifier": None, "action": select_object},
            {"title": "Select Window", "button": "LEFT", "modifier": "SHIFT", "action": select_window},
        ]
    )


@dataclass
class WheelEvents:
    items: list[dict] = field(
        default_factory=lambda: [
            {"title": "Zoom View", "action": zoom_view},
        ]
    )


@dataclass
class Config(ConfigBase):
    ui: UIConfig = field(default_factory=UIConfig)
    window: WindowConfig = field(default_factory=WindowConfig)
    renderer: RendererConfig = field(default_factory=RendererConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    selector: SelectorConfig = field(default_factory=SelectorConfig)
    key_events: KeyEvents = field(default_factory=KeyEvents)
    mouse_events: MouseEvents = field(default_factory=MouseEvents)
    wheel_events: WheelEvents = field(default_factory=WheelEvents)
