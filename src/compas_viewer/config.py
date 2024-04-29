import json
from dataclasses import dataclass
from dataclasses import field
from dataclasses import is_dataclass
from typing import Literal

from compas.colors import Color


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
class View3dConfig(Base):
    viewport: Literal["top", "perspective"] = "perspective"
    background: Color = field(default_factory=lambda: Color.from_hex("#eeeeee"))
    show_grid: bool = True
    show_axes: bool = True
    camera: CameraConfig = field(default_factory=CameraConfig)


@dataclass
class ToolbarConfig(Base):
    show: bool = True
    items: list[dict[str, str]] = None


@dataclass
class MenubarConfig(Base):
    show: bool = True
    items: list[dict[str, str]] = None


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


@dataclass
class ControllerConfig(Base):
    pass


@dataclass
class Config(Base):
    ui: UIConfig = field(default_factory=UIConfig)
    window: WindowConfig = field(default_factory=WindowConfig)
    controller: ControllerConfig = field(default_factory=ControllerConfig)


if __name__ == "__main__":
    config = Config.from_json("src/compas_viewer/config.json")

    print("Full config:")
    print(config)

    print("\nWindow config:")
    print(config.window)
