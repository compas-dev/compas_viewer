import json
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import is_dataclass
from functools import partial
from typing import Literal

from compas.colors import Color
from compas_viewer._actions import change_viewmode
from compas_viewer._actions import open_camera_settings_dialog


class Base:
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


@dataclass
class CameraConfig(Base):
    position: list[float] = field(default_factory=lambda: [10, 10, 10])
    target: list[float] = field(default_factory=lambda: [0, 0, 0])
    up: list[float] = field(default_factory=lambda: [0, 0, 1])
    near: float = 0.1
    far: float = 1000
    fov: float = 50


@dataclass
class DisplayConfig(Base):
    pointcolor: Color = field(default_factory=Color.black)
    linecolor: Color = field(default_factory=Color.black)
    surfacecolor: Color = field(default_factory=Color.grey)
    pointsize: float = float(6.0)
    linewidth: float = float(1.0)
    opacity: float = float(1.0)


@dataclass
class View3dConfig(Base):
    viewport: Literal["top", "perspective"] = "perspective"
    background: Color = field(default_factory=lambda: Color.from_hex("#eeeeee"))
    show_grid: bool = True
    show_axes: bool = True
    camera: CameraConfig = field(default_factory=CameraConfig)


@dataclass
class ToolbarConfig(Base):
    show: bool = True
    items: list[dict[str, str]] = field(
        default_factory=lambda: [
            {
                "type": "select",
                "action": change_viewmode,
                "items": [
                    {"title": "Perspective", "value": "perspective"},
                    {"title": "Top", "value": "top"},
                    {"title": "Front", "value": "front"},
                    {"title": "Right", "value": "right"},
                ],
            },
        ]
    )


@dataclass
class MenubarConfig(Base):
    show: bool = True
    items: list[dict[str, str]] = field(
        default_factory=lambda: [
            {
                "title": "Test",
                "items": [
                    {"title": "a", "action": lambda: print("a")},
                    {"title": "b", "action": lambda: print("b")},
                ],
            },
            {
                "title": "Camera",
                "items": [
                    {"title": "Target and Position", "action": open_camera_settings_dialog},
                    {
                        "title": "Viewmode",
                        "items": [
                            {"title": "Perspective", "action": partial(change_viewmode, "perspective")},
                            {"title": "Top", "action": partial(change_viewmode, "top")},
                            {"title": "Front", "action": partial(change_viewmode, "front")},
                            {"title": "Left", "action": partial(change_viewmode, "left")},
                        ],
                    },
                ],
            },
        ]
    )


@dataclass
class StatusbarConfig(Base):
    show: bool = True
    items: list[dict[str, str]] = None


@dataclass
class SidebarConfig(Base):
    show: bool = True
    items: list[dict[str, str]] = None


@dataclass
class WindowConfig(Base):
    title: str = "COMPAS Viewer"
    width: int = 1280
    height: int = 720
    fullscreen: bool = False
    about: str = "Stand-alone viewer for COMPAS."


@dataclass
class UIConfig(Base):
    menubar: MenubarConfig = field(default_factory=MenubarConfig)
    toolbar: ToolbarConfig = field(default_factory=ToolbarConfig)
    statusbar: StatusbarConfig = field(default_factory=StatusbarConfig)
    sidebar: SidebarConfig = field(default_factory=SidebarConfig)
    view3d: View3dConfig = field(default_factory=View3dConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)


@dataclass
class RendererConfig(Base):
    show_grid: bool = True
    show_gridz: bool = True
    gridsize: tuple[float, int, float, int] = field(default_factory=lambda: (10.0, 10, 10.0, 10))
    opacity: float = 1.0
    ghostopacity: float = 0.7
    rendermode: Literal["ghosted", "shaded", "lighted", "wireframe"] = "shaded"
    viewmode: Literal["perspective", "front", "right", "top"] = "perspective"
    backgroundcolor: Color = field(default_factory=Color.white)


@dataclass
class CameraConfig(Base):
    fov: float = 45.0
    near: float = 0.1
    far: float = 1000.0
    position: list[float] = field(default_factory=lambda: [10.0, 10.0, 10.0])
    target: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    scale: float = 1.0
    zoomdelta: float = 0.05
    rotationdelta: float = 0.01
    pan_delta: float = 0.05


@dataclass
class SelectorConfig(Base):
    enable: bool = True
    selectioncolor: Color = field(default_factory=lambda: Color(1.0, 1.0, 0.0, 1.0))


@dataclass
class MouseEvent:
    mouse: str
    modifier: str = "no"


@dataclass
class MouseEventConfig(Base):
    pan: MouseEvent = field(default_factory=lambda: MouseEvent(mouse="right", modifier="shift"))
    rotate: MouseEvent = field(default_factory=lambda: MouseEvent(mouse="right"))
    drag_selection: MouseEvent = field(default_factory=lambda: MouseEvent(mouse="left"))
    drag_deselection: MouseEvent = field(default_factory=lambda: MouseEvent(mouse="left", modifier="control"))
    multiselect: MouseEvent = field(default_factory=lambda: MouseEvent(mouse="left", modifier="shift"))
    deselect: MouseEvent = field(default_factory=lambda: MouseEvent(mouse="left", modifier="control"))


@dataclass
class KeyEvent:
    key: str
    modifier: str = "no"


@dataclass
class KeyEventConfig(Base):
    zoom_selected: KeyEvent = field(default_factory=lambda: KeyEvent(key="f"))
    gl_info: KeyEvent = field(default_factory=lambda: KeyEvent(key="i"))
    select_all: KeyEvent = field(default_factory=lambda: KeyEvent(key="a", modifier="control"))
    view_top: KeyEvent = field(default_factory=lambda: KeyEvent(key="f3"))
    view_perspective: KeyEvent = field(default_factory=lambda: KeyEvent(key="f4"))
    view_front: KeyEvent = field(default_factory=lambda: KeyEvent(key="f5"))
    view_right: KeyEvent = field(default_factory=lambda: KeyEvent(key="f6"))
    delete_selected: KeyEvent = field(default_factory=lambda: KeyEvent(key="delete"))
    camera_info: KeyEvent = field(default_factory=lambda: KeyEvent(key="c"))
    selection_info: KeyEvent = field(default_factory=lambda: KeyEvent(key="s"))


@dataclass
class Config(Base):
    ui: UIConfig = field(default_factory=UIConfig)
    window: WindowConfig = field(default_factory=WindowConfig)
    renderer: RendererConfig = field(default_factory=RendererConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    selector: SelectorConfig = field(default_factory=SelectorConfig)
    mouse_event: MouseEventConfig = field(default_factory=MouseEventConfig)
    key_event: KeyEventConfig = field(default_factory=KeyEventConfig)


if __name__ == "__main__":
    config = Config()

    print(asdict(config.key_event).items())
