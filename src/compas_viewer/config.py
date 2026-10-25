import json
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from pathlib import Path
from typing import Any
from typing import Literal
from typing import Self
from typing import get_args
from typing import get_origin
from typing import get_type_hints

from compas.colors import Color

type Unit = Literal["m", "cm", "mm"]
type Appearance = Literal["system", "light", "dark"]


def _default_backgroundcolor() -> Color:
    return Color.white()


def _serialize_config_value(value: Any) -> Any:
    if isinstance(value, ConfigBase):
        return value.to_dict()
    if isinstance(value, Color):
        return {"__color__": list(value.rgba)}
    if callable(value):
        raise TypeError("Runtime callbacks cannot be stored in viewer configuration.")
    if isinstance(value, dict):
        data: dict[str, Any] = {}
        for key, item in value.items():
            data[str(key)] = _serialize_config_value(item)
        return data
    if isinstance(value, (list, tuple)):
        items: list[Any] = []
        for item in value:
            items.append(_serialize_config_value(item))
        return items
    return value


def _deserialize_config_value(annotation: Any, value: Any) -> Any:
    if isinstance(value, dict) and "__color__" in value:
        red, green, blue, alpha = value["__color__"]
        return Color(red=red, green=green, blue=blue, alpha=alpha)

    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is tuple and isinstance(value, list):
        return tuple(value)
    if origin is list and isinstance(value, list) and args:
        return [_deserialize_config_value(args[0], item) for item in value]
    if isinstance(annotation, type) and issubclass(annotation, ConfigBase) and isinstance(value, dict):
        return annotation.from_dict(value)
    return value


class ConfigBase:
    """Provide JSON and dictionary serialization for viewer configuration."""

    @classmethod
    def from_json(cls, filepath: str | Path) -> Self:
        """Create a configuration from a JSON file.

        Parameters
        ----------
        filepath
            Path to the JSON configuration file.

        Returns
        -------
        ConfigBase
            A configuration of the requested class.

        """
        with Path(filepath).open(encoding="utf-8") as fp:
            data: dict[str, Any] = json.load(fp)
        return cls.from_dict(data)

    def to_json(self, filepath: str | Path) -> None:
        """Write the configuration to a JSON file.

        Parameters
        ----------
        filepath
            Destination path for the JSON configuration file.

        """
        with Path(filepath).open("w", encoding="utf-8") as fp:
            json.dump(self.to_dict(), fp, indent=4)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a configuration from a dictionary.

        Parameters
        ----------
        data
            Configuration values keyed by field name.

        Returns
        -------
        ConfigBase
            A configuration of the requested class.

        """
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        """Convert the configuration to a dictionary.

        Returns
        -------
        dict[str, Any]
            Public configuration values keyed by field name.

        """
        data: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                data[key] = _serialize_config_value(value)
        return data

    def __post_init__(self) -> None:
        annotations = get_type_hints(type(self))
        for config_field in fields(self):  # type: ignore[arg-type]
            value = getattr(self, config_field.name)
            annotation = annotations.get(config_field.name, config_field.type)
            setattr(self, config_field.name, _deserialize_config_value(annotation, value))


# =============================================================================
# =============================================================================
# =============================================================================
# Window
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class WindowConfig(ConfigBase):
    """Configure the main viewer window."""

    title: str = "COMPAS Viewer"
    width: int = 1280
    height: int = 720
    fullscreen: bool = False
    about: str = "Stand-alone viewer for COMPAS."


# =============================================================================
# =============================================================================
# =============================================================================
# ToolBar
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class ToolbarConfig(ConfigBase):
    """Configure the viewer toolbar."""

    show: bool = False


# =============================================================================
# =============================================================================
# =============================================================================
# MenuBar
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class MenubarConfig(ConfigBase):
    """Configure the viewer menu bar."""

    show: bool = True


# =============================================================================
# =============================================================================
# =============================================================================
# StatusBar
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class StatusbarConfig(ConfigBase):
    """Configure the viewer status bar."""

    show: bool = True


# =============================================================================
# =============================================================================
# =============================================================================
# SideBar
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class SidebarConfig(ConfigBase):
    """Configure the viewer sidebar."""

    show: bool = True
    width: int = 320
    minimum_width: int = 240
    show_widgets: bool = True
    sceneform: bool = True


# =============================================================================
# =============================================================================
# =============================================================================
# SideDock
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class SidedockConfig(ConfigBase):
    """Configure the viewer side dock."""

    show: bool = False


# =============================================================================
# =============================================================================
# =============================================================================
# View3D
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class DisplayConfig(ConfigBase):
    """Configure default scene-object display properties."""

    pointcolor: Color = field(default_factory=Color.black)
    linecolor: Color = field(default_factory=Color.black)
    surfacecolor: Color = field(default_factory=Color.grey)
    pointsize: float = float(6.0)
    linewidth: float = float(1.0)
    opacity: float = float(1.0)


@dataclass
class RendererConfig(ConfigBase):
    """Configure rendering, grids, views, and selection styling."""

    show_grid: bool = True
    show_gridz: bool = False
    gridmode: Literal["full", "quadrant"] = "full"
    gridsize: tuple[float, int, float, int] = field(default_factory=lambda: (10.0, 10, 10.0, 10))
    gridcolor: Color = field(default_factory=lambda: Color(0.7, 0.7, 0.7))
    opacity: float = 1.0
    ghostopacity: float = 0.7
    rendermode: Literal["ghosted", "shaded", "lighted", "wireframe"] = "shaded"
    view: Literal["perspective", "front", "right", "top"] = "perspective"
    backgroundcolor: Color = field(default_factory=_default_backgroundcolor)
    selectioncolor: Color = field(default_factory=lambda: Color(1.0, 1.0, 0.0, 1.0))
    debug_instance: bool = False


@dataclass
class CameraConfig(ConfigBase):
    """Configure the viewer camera."""

    fov: float = 45.0
    near: float = 0.1
    far: float = 1000.0
    position: list[float] = field(default_factory=lambda: [-10.0, -10.0, 10.0])
    target: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    scale: float = 1.0
    zoomdelta: float = 0.05
    rotationdelta: float = 0.01
    pandelta: float = 0.05


# =============================================================================
# =============================================================================
# =============================================================================
# UI
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class UIConfig(ConfigBase):
    """Group configuration for the viewer interface components."""

    appearance: Appearance = "system"
    menubar: MenubarConfig = field(default_factory=MenubarConfig)
    toolbar: ToolbarConfig = field(default_factory=ToolbarConfig)
    statusbar: StatusbarConfig = field(default_factory=StatusbarConfig)
    sidebar: SidebarConfig = field(default_factory=SidebarConfig)
    sidedock: SidedockConfig = field(default_factory=SidedockConfig)


# =============================================================================
# =============================================================================
# =============================================================================
# Events
# =============================================================================
# =============================================================================
# =============================================================================

# =============================================================================
# =============================================================================
# =============================================================================
# Config
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class Config(ConfigBase):
    """Collect the complete viewer configuration."""

    schema_version: int = 1
    vectorsize: float = 0.1
    unit: Unit = "m"
    ui: UIConfig = field(default_factory=UIConfig)
    window: WindowConfig = field(default_factory=WindowConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    renderer: RendererConfig = field(default_factory=RendererConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a configuration and migrate supported legacy fields.

        Parameters
        ----------
        data
            Serialized configuration values.

        Returns
        -------
        Config
            Migrated viewer configuration.

        Raises
        ------
        ValueError
            If the configuration schema is newer than this viewer supports.

        """
        migrated = dict(data)
        version = migrated.get("schema_version", 0)
        if not isinstance(version, int) or version > 1:
            raise ValueError(f"Unsupported configuration schema version: {version!r}.")

        migrated.pop("commands", None)
        ui = dict(migrated.get("ui", {}))
        for section in ("menubar", "toolbar", "statusbar", "sidebar", "sidedock"):
            values = ui.get(section)
            if isinstance(values, dict):
                values = dict(values)
                values.pop("items", None)
                ui[section] = values
        ui.pop("view3d", None)
        if "display" in ui and "display" not in migrated:
            migrated["display"] = ui.pop("display")
        migrated["ui"] = ui
        migrated["schema_version"] = 1
        return cls(**migrated)
