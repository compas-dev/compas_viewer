import json
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from math import isfinite
from pathlib import Path
from typing import Any
from typing import Literal
from typing import Self
from typing import get_args
from typing import get_origin
from typing import get_type_hints

from compas.colors import Color

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


def _path(parent: str, name: str) -> str:
    return f"{parent}.{name}" if parent else name


def _require_bool(path: str, value: object) -> None:
    if not isinstance(value, bool):
        raise TypeError(f"{path} should be a boolean.")


def _require_int(path: str, value: object, *, positive: bool = False) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{path} should be an integer.")
    if positive and value <= 0:
        raise ValueError(f"{path} should be positive.")


def _require_number(path: str, value: object, *, positive: bool = False, minimum: float | None = None, maximum: float | None = None) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{path} should be a number.")
    if isinstance(value, float) and not isfinite(value):
        raise ValueError(f"{path} should be finite.")
    if positive and value <= 0:
        raise ValueError(f"{path} should be positive.")
    if minimum is not None and value < minimum:
        raise ValueError(f"{path} should be at least {minimum}.")
    if maximum is not None and value > maximum:
        raise ValueError(f"{path} should be at most {maximum}.")


def _require_choice(path: str, value: object, choices: set[str]) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{path} should be a string.")
    if value not in choices:
        raise ValueError(f"{path} should be one of: {', '.join(sorted(choices))}.")


def _require_color(path: str, value: object) -> None:
    if not isinstance(value, Color):
        raise TypeError(f"{path} should be a Color.")
    for index, component in enumerate(value.rgba):
        _require_number(f"{path}[{index}]", component, minimum=0.0, maximum=1.0)


def _require_vector(path: str, value: object) -> None:
    if not isinstance(value, list):
        raise TypeError(f"{path} should be a list of numbers.")
    if len(value) != 3:
        raise ValueError(f"{path} should contain exactly three numbers.")
    for index, coordinate in enumerate(value):
        _require_number(f"{path}[{index}]", coordinate)


def _deserialize_config_value(annotation: Any, value: Any, path: str) -> Any:
    if isinstance(value, dict) and "__color__" in value:
        if set(value) != {"__color__"}:
            raise ValueError(f"{path} contains an invalid color encoding.")
        components = value["__color__"]
        if not isinstance(components, list) or len(components) != 4:
            raise ValueError(f"{path} should encode exactly four color components.")
        for index, component in enumerate(components):
            _require_number(f"{path}[{index}]", component, minimum=0.0, maximum=1.0)
        red, green, blue, alpha = components
        return Color(red=red, green=green, blue=blue, alpha=alpha)

    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is tuple and isinstance(value, list):
        return tuple(value)
    if origin is list and isinstance(value, list) and args:
        return [_deserialize_config_value(args[0], item, path) for item in value]
    if isinstance(annotation, type) and issubclass(annotation, ConfigBase) and isinstance(value, dict):
        return annotation._from_dict(value, path)
    return value


class ConfigBase:
    """Provide closed JSON and dictionary serialization for a config group.

    Only declared dataclass fields are serialized. Subclasses should implement
    `validate` when they add values with constraints. Unknown fields are
    rejected when loading serialized data, and runtime callbacks cannot be
    serialized.

    """

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
        path = cls.__name__.removesuffix("Config").lower() or "config"
        return cls._from_dict(data, path)

    @classmethod
    def _from_dict(cls, data: dict[str, Any], path: str) -> Self:
        if not isinstance(data, dict):
            raise TypeError(f"{path} should be a mapping.")
        declared = {config_field.name for config_field in fields(cls)}  # type: ignore[arg-type]
        unknown = sorted(set(data) - declared)
        if unknown:
            names = ", ".join(_path(path, name) for name in unknown)
            raise ValueError(f"Unknown configuration fields: {names}.")
        annotations = get_type_hints(cls)
        kwargs: dict[str, Any] = {}
        for config_field in fields(cls):  # type: ignore[arg-type]
            if config_field.name in data:
                annotation = annotations.get(config_field.name, config_field.type)
                kwargs[config_field.name] = _deserialize_config_value(annotation, data[config_field.name], _path(path, config_field.name))
        obj = cls(**kwargs)
        obj.validate(path)
        return obj

    def to_dict(self) -> dict[str, Any]:
        """Convert the configuration to a dictionary.

        Returns
        -------
        dict[str, Any]
            Public configuration values keyed by field name.

        """
        return {
            config_field.name: _serialize_config_value(getattr(self, config_field.name))
            for config_field in fields(self)  # type: ignore[arg-type]
        }

    def validate(self, path: str = "config") -> None:
        """Validate this configuration group.

        Parameters
        ----------
        path
            Full configuration path used in validation errors.

        """

    def __post_init__(self) -> None:
        annotations = get_type_hints(type(self))
        for config_field in fields(self):  # type: ignore[arg-type]
            value = getattr(self, config_field.name)
            annotation = annotations.get(config_field.name, config_field.type)
            setattr(self, config_field.name, _deserialize_config_value(annotation, value, config_field.name))


# =============================================================================
# =============================================================================
# =============================================================================
# Window
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class WindowConfig(ConfigBase):
    """Configure the main viewer window at startup.

    Parameters
    ----------
    title
        Non-empty Qt application and main-window title.
    icon
        Absolute path to an existing icon file. If `None`, Viewer uses the
        packaged COMPAS icon.
    width
        Initial window width in pixels.
    height
        Initial window height in pixels.
    fullscreen
        Whether to start the Viewer in fullscreen mode.

    Notes
    -----
    Viewer validates and applies these values during construction. Changing
    them afterward has no promised live effect.

    """

    title: str = "COMPAS Viewer"
    icon: str | None = None
    width: int = 1280
    height: int = 720
    fullscreen: bool = False

    def validate(self, path: str = "window") -> None:
        if not isinstance(self.title, str):
            raise TypeError(f"{path}.title should be a string.")
        if not self.title:
            raise ValueError(f"{path}.title should be a non-empty string.")
        if self.icon is not None:
            if not isinstance(self.icon, str):
                raise TypeError(f"{path}.icon should be an absolute path string or None.")
            icon = Path(self.icon)
            if not icon.is_absolute():
                raise ValueError(f"{path}.icon should be an absolute filesystem path.")
            if not icon.is_file():
                raise ValueError(f"{path}.icon does not identify an existing file: {icon}.")
        _require_int(f"{path}.width", self.width, positive=True)
        _require_int(f"{path}.height", self.height, positive=True)
        _require_bool(f"{path}.fullscreen", self.fullscreen)


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

    def validate(self, path: str = "ui.toolbar") -> None:
        _require_bool(f"{path}.show", self.show)


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

    def validate(self, path: str = "ui.menubar") -> None:
        _require_bool(f"{path}.show", self.show)


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

    def validate(self, path: str = "ui.statusbar") -> None:
        _require_bool(f"{path}.show", self.show)


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

    def validate(self, path: str = "ui.sidebar") -> None:
        _require_bool(f"{path}.show", self.show)
        _require_int(f"{path}.width", self.width, positive=True)
        _require_int(f"{path}.minimum_width", self.minimum_width, positive=True)


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

    def validate(self, path: str = "ui.sidedock") -> None:
        _require_bool(f"{path}.show", self.show)


# =============================================================================
# =============================================================================
# =============================================================================
# View3D
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class RendererConfig(ConfigBase):
    """Configure rendering, grids, views, and selection styling."""

    show_grid: bool = True
    show_gridz: bool = False
    gridmode: Literal["full", "quadrant"] = "full"
    gridsize: tuple[float, int, float, int] = field(default_factory=lambda: (10.0, 10, 10.0, 10))
    gridcolor: Color = field(default_factory=lambda: Color(0.7, 0.7, 0.7))
    ghostopacity: float = 0.7
    rendermode: Literal["ghosted", "shaded", "lighted", "wireframe"] = "shaded"
    view: Literal["perspective", "front", "right", "top", "ortho"] = "perspective"
    backgroundcolor: Color = field(default_factory=_default_backgroundcolor)
    selectioncolor: Color = field(default_factory=lambda: Color(1.0, 1.0, 0.0, 1.0))
    debug_instance: bool = False

    def validate(self, path: str = "renderer") -> None:
        _require_bool(f"{path}.show_grid", self.show_grid)
        _require_bool(f"{path}.show_gridz", self.show_gridz)
        _require_choice(f"{path}.gridmode", self.gridmode, {"full", "quadrant"})
        if not isinstance(self.gridsize, tuple):
            raise TypeError(f"{path}.gridsize should be a tuple.")
        if len(self.gridsize) != 4:
            raise ValueError(f"{path}.gridsize should contain four values.")
        dx, nx, dy, ny = self.gridsize
        _require_number(f"{path}.gridsize[0]", dx, positive=True)
        _require_int(f"{path}.gridsize[1]", nx, positive=True)
        _require_number(f"{path}.gridsize[2]", dy, positive=True)
        _require_int(f"{path}.gridsize[3]", ny, positive=True)
        _require_color(f"{path}.gridcolor", self.gridcolor)
        _require_number(f"{path}.ghostopacity", self.ghostopacity, minimum=0.0, maximum=1.0)
        _require_choice(f"{path}.rendermode", self.rendermode, {"ghosted", "lighted", "shaded", "wireframe"})
        _require_choice(f"{path}.view", self.view, {"front", "ortho", "perspective", "right", "top"})
        _require_color(f"{path}.backgroundcolor", self.backgroundcolor)
        _require_color(f"{path}.selectioncolor", self.selectioncolor)
        _require_bool(f"{path}.debug_instance", self.debug_instance)


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

    def validate(self, path: str = "camera") -> None:
        _require_number(f"{path}.fov", self.fov, positive=True, maximum=179.0)
        _require_number(f"{path}.near", self.near, positive=True)
        _require_number(f"{path}.far", self.far, positive=True)
        if self.far <= self.near:
            raise ValueError(f"{path}.far should be greater than {path}.near.")
        _require_vector(f"{path}.position", self.position)
        _require_vector(f"{path}.target", self.target)
        _require_number(f"{path}.scale", self.scale, positive=True)
        _require_number(f"{path}.zoomdelta", self.zoomdelta, positive=True)
        _require_number(f"{path}.rotationdelta", self.rotationdelta, positive=True)
        _require_number(f"{path}.pandelta", self.pandelta, positive=True)


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

    def validate(self, path: str = "ui") -> None:
        _require_choice(f"{path}.appearance", self.appearance, {"dark", "light", "system"})
        sections = {
            "menubar": (self.menubar, MenubarConfig),
            "toolbar": (self.toolbar, ToolbarConfig),
            "statusbar": (self.statusbar, StatusbarConfig),
            "sidebar": (self.sidebar, SidebarConfig),
            "sidedock": (self.sidedock, SidedockConfig),
        }
        for name, (value, expected) in sections.items():
            if not isinstance(value, expected):
                raise TypeError(f"{path}.{name} should be a {expected.__name__}.")
            value.validate(f"{path}.{name}")


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
    """Collect validated, serializable Viewer startup preferences.

    Nested values may be assigned directly while preparing a Viewer. They do
    not provide a general reactive runtime interface. Schema version 2 accepts
    only declared fields. `Config.from_dict` also migrates supported version-0
    and version-1 data by discarding known retired fields.

    """

    schema_version: int = 2
    vectorsize: float = 0.1
    ui: UIConfig = field(default_factory=UIConfig)
    window: WindowConfig = field(default_factory=WindowConfig)
    renderer: RendererConfig = field(default_factory=RendererConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)

    def validate(self, path: str = "") -> None:
        """Validate the complete configuration.

        Parameters
        ----------
        path
            Optional prefix used in validation errors.

        """
        _require_int(_path(path, "schema_version"), self.schema_version)
        if self.schema_version != 2:
            raise ValueError(f"{_path(path, 'schema_version')} should be 2.")
        _require_number(_path(path, "vectorsize"), self.vectorsize, positive=True)

        sections = {
            "ui": (self.ui, UIConfig),
            "window": (self.window, WindowConfig),
            "renderer": (self.renderer, RendererConfig),
            "camera": (self.camera, CameraConfig),
        }
        for name, (value, expected) in sections.items():
            section_path = _path(path, name)
            if not isinstance(value, expected):
                raise TypeError(f"{section_path} should be a {expected.__name__}.")
            value.validate(section_path)

        core_fields = {"schema_version", "vectorsize", "ui", "window", "renderer", "camera"}
        annotations = get_type_hints(type(self))
        for config_field in fields(self):
            if config_field.name in core_fields:
                continue
            value = getattr(self, config_field.name)
            expected = annotations.get(config_field.name, config_field.type)
            if isinstance(expected, type) and issubclass(expected, ConfigBase):
                section_path = _path(path, config_field.name)
                if not isinstance(value, expected):
                    raise TypeError(f"{section_path} should be a {expected.__name__}.")
                value.validate(section_path)

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
        TypeError
            If the input or a declared value has the wrong type.
        ValueError
            If the schema is unsupported, a field is unknown, or a value is
            outside its accepted range.

        """
        if not isinstance(data, dict):
            raise TypeError("config should be a mapping.")

        migrated = dict(data)
        version = migrated.get("schema_version", 0)
        if isinstance(version, bool) or not isinstance(version, int) or version not in {0, 1, 2}:
            raise ValueError(f"Unsupported configuration schema version: {version!r}.")

        if version < 2:
            for name in ("commands", "display", "unit"):
                migrated.pop(name, None)

            window = migrated.get("window")
            if isinstance(window, dict):
                window = dict(window)
                window.pop("about", None)
                migrated["window"] = window

            renderer = migrated.get("renderer")
            if isinstance(renderer, dict):
                renderer = dict(renderer)
                renderer.pop("opacity", None)
                migrated["renderer"] = renderer

            ui = migrated.get("ui")
            if isinstance(ui, dict):
                ui = dict(ui)
                ui.pop("display", None)
                ui.pop("view3d", None)
                for section in ("menubar", "toolbar", "statusbar", "sidebar", "sidedock"):
                    values = ui.get(section)
                    if isinstance(values, dict):
                        values = dict(values)
                        values.pop("items", None)
                        if section == "sidebar":
                            values.pop("show_widgets", None)
                            values.pop("sceneform", None)
                        ui[section] = values
                migrated["ui"] = ui

            migrated["schema_version"] = 2

        return cls._from_dict(migrated, "")
