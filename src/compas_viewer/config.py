import json
from dataclasses import dataclass
from dataclasses import field
from dataclasses import is_dataclass
from typing import Literal

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

from compas.colors import Color
from compas_viewer.commands import Command
from compas_viewer.commands import camera_settings_cmd
from compas_viewer.commands import capture_view_cmd
from compas_viewer.commands import change_rendermode_cmd
from compas_viewer.commands import change_view_cmd
from compas_viewer.commands import clear_scene_cmd
from compas_viewer.commands import deselect_all_cmd
from compas_viewer.commands import load_scene_cmd
from compas_viewer.commands import obj_settings_cmd
from compas_viewer.commands import pan_view_cmd
from compas_viewer.commands import rotate_view_cmd
from compas_viewer.commands import save_scene_cmd
from compas_viewer.commands import select_all_cmd
from compas_viewer.commands import select_object_cmd
from compas_viewer.commands import select_window_cmd
from compas_viewer.commands import toggle_sidebar_cmd
from compas_viewer.commands import toggle_sidedock_cmd
from compas_viewer.commands import toggle_statusbar_cmd
from compas_viewer.commands import toggle_toolbar_cmd
from compas_viewer.commands import zoom_selected_cmd
from compas_viewer.commands import zoom_view_cmd


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


# =============================================================================
# =============================================================================
# =============================================================================
# Window
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class WindowConfig(ConfigBase):
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
    show: bool = False
    items: list[dict] = field(default_factory=lambda: [])


# =============================================================================
# =============================================================================
# =============================================================================
# MenuBar
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class MenubarConfig(ConfigBase):
    show: bool = True
    items: list[dict] = field(
        default_factory=lambda: [
            {
                "title": "View",
                "items": [
                    {"title": toggle_toolbar_cmd.title, "type": "checkbox", "checked": lambda viewer: viewer.config.ui.toolbar.show, "action": toggle_toolbar_cmd},
                    {"title": toggle_sidebar_cmd.title, "type": "checkbox", "checked": lambda viewer: viewer.config.ui.sidebar.show, "action": toggle_sidebar_cmd},
                    {"title": toggle_sidedock_cmd.title, "type": "checkbox", "checked": lambda viewer: viewer.config.ui.sidedock.show, "action": toggle_sidedock_cmd},
                    {"title": toggle_statusbar_cmd.title, "type": "checkbox", "checked": lambda viewer: viewer.config.ui.statusbar.show, "action": toggle_statusbar_cmd},
                    {"type": "separator"},
                    {
                        "title": "Set Render Mode",
                        "type": "group",
                        "exclusive": True,
                        "selected": 0,
                        "items": [
                            {"title": "Shaded", "action": change_rendermode_cmd, "kwargs": {"mode": "shaded"}},
                            {"title": "Ghosted", "action": change_rendermode_cmd, "kwargs": {"mode": "ghosted"}},
                            {"title": "Lighted", "action": change_rendermode_cmd, "kwargs": {"mode": "lighted"}},
                            {"title": "Wireframe", "action": change_rendermode_cmd, "kwargs": {"mode": "wireframe"}},
                        ],
                    },
                    {
                        "title": "Set Current View",
                        "type": "group",
                        "exclusive": True,
                        "checked": 0,
                        "items": [
                            {"title": "Perspective", "action": change_view_cmd, "kwargs": {"mode": "perspective"}},
                            {"title": "Top", "action": change_view_cmd, "kwargs": {"mode": "top"}},
                            {"title": "Front", "action": change_view_cmd, "kwargs": {"mode": "front"}},
                            {"title": "Right", "action": change_view_cmd, "kwargs": {"mode": "right"}},
                        ],
                    },
                    {"type": "separator"},
                    {"title": camera_settings_cmd.title, "action": camera_settings_cmd},
                    {"title": "Display Settings", "action": lambda: print("Display Settings")},
                    {"title": capture_view_cmd.title, "action": capture_view_cmd},
                    {"type": "separator"},
                ],
            },
            {
                "title": "Edit",
                "items": [],
            },
            {
                "title": "Select",
                "items": [
                    {"title": select_all_cmd.title, "action": select_all_cmd},
                    {"title": "Invert Selection", "action": lambda: print("invert selection")},
                    {"type": "separator"},
                    {"title": deselect_all_cmd.title, "action": deselect_all_cmd},
                ],
            },
            {
                "title": "Scene",
                "items": [
                    {"title": clear_scene_cmd.title, "action": clear_scene_cmd},
                    {"type": "separator"},
                    {"title": load_scene_cmd.title, "action": load_scene_cmd},
                    {"title": save_scene_cmd.title, "action": save_scene_cmd},
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
                "title": "Info",
                "items": [
                    {"title": "Selected obj info", "action": obj_settings_cmd},
                ],
            },
            {
                "title": "Server/Session",
                "items": [],
            },
            {
                "title": "Help",
                "items": [
                    {"title": "Viewer Docs", "action": lambda: QDesktopServices.openUrl(QUrl("https://compas.dev/compas_viewer"))},
                    {"title": "Viewer Github", "action": lambda: QDesktopServices.openUrl(QUrl("https://github.com/compas-dev/compas_viewer"))},
                    {"type": "separator"},
                    {"title": "COMPAS Home", "action": lambda: QDesktopServices.openUrl(QUrl("https://compas.dev/"))},
                    {"title": "COMPAS Docs", "action": lambda: QDesktopServices.openUrl(QUrl("https://compas.dev/compas"))},
                    {"title": "COMPAS Github", "action": lambda: QDesktopServices.openUrl(QUrl("https://github.com/compas-dev/compas"))},
                ],
            },
        ]
    )


# =============================================================================
# =============================================================================
# =============================================================================
# StatusBar
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class StatusbarConfig(ConfigBase):
    show: bool = True
    items: list[dict[str, str]] = None


# =============================================================================
# =============================================================================
# =============================================================================
# SideBar
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class SidebarConfig(ConfigBase):
    show: bool = True
    show_widgets: bool = True
    sceneform: bool = True
    items: list[dict] = field(
        default_factory=lambda: [
            {
                "type": "Sceneform",
                "columns": [
                    {"title": "Name", "type": "label", "text": lambda obj: obj.name},
                    {"title": "Show", "type": "checkbox", "checked": lambda obj: obj.show, "action": lambda obj, checked: setattr(obj, "show", checked)},
                ],
            },
            {
                "type": "ObjectSetting",
                "items": [
                    {"title": "Name", "items": [{"type": "text_edit", "action": lambda obj: obj.name}]},
                    {"title": "Point_Color", "items": [{"type": "color_dialog", "attr": "pointcolor"}]},
                    {"title": "Line_Color", "items": [{"type": "color_dialog", "attr": "linecolor"}]},
                    {"title": "Face_Color", "items": [{"type": "color_dialog", "attr": "facecolor"}]},
                    {"title": "Line_Width", "items": [{"type": "double_edit", "action": lambda obj: obj.linewidth, "min_val": 0.0, "max_val": 10.0}]},
                    {"title": "Point_Size", "items": [{"type": "double_edit", "action": lambda obj: obj.pointsize, "min_val": 0.0, "max_val": 10.0}]},
                    {"title": "Opacity", "items": [{"type": "double_edit", "action": lambda obj: obj.opacity, "min_val": 0.0, "max_val": 1.0}]},
                ],
            },
        ]
    )


# =============================================================================
# =============================================================================
# =============================================================================
# SideDock
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class SidedockConfig(ConfigBase):
    show: bool = False
    items: list[dict[str, str]] = None


# =============================================================================
# =============================================================================
# =============================================================================
# View3D
# =============================================================================
# =============================================================================
# =============================================================================


# this should be part of View3D config
@dataclass
class DisplayConfig(ConfigBase):
    pointcolor: Color = field(default_factory=Color.black)
    linecolor: Color = field(default_factory=Color.black)
    surfacecolor: Color = field(default_factory=Color.grey)
    pointsize: float = float(6.0)
    linewidth: float = float(1.0)
    opacity: float = float(1.0)


# this should be part of View3D config
@dataclass
class RendererConfig(ConfigBase):
    show_grid: bool = True
    show_gridz: bool = False
    gridmode: Literal["full", "quadrant"] = "full"
    gridsize: tuple[float, int, float, int] = field(default_factory=lambda: (10.0, 10, 10.0, 10))
    gridcolor: Color = field(default_factory=lambda: Color(0.7, 0.7, 0.7))
    opacity: float = 1.0
    ghostopacity: float = 0.7
    rendermode: Literal["ghosted", "shaded", "lighted", "wireframe"] = "shaded"
    view: Literal["perspective", "front", "right", "top"] = "perspective"
    backgroundcolor: Color = field(default_factory=Color.white)
    selectioncolor: Color = field(default_factory=lambda: Color(1.0, 1.0, 0.0, 1.0))


# this should be part of View3D config
@dataclass
class CameraConfig(ConfigBase):
    fov: float = 45.0
    near: float = 0.1
    far: float = 1000.0
    position: list[float] = field(default_factory=lambda: [-10.0, -10.0, 10.0])
    target: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    scale: float = 1.0
    zoomdelta: float = 0.05
    rotationdelta: float = 0.01
    pandelta: float = 0.05


@dataclass
class CameraDialogConfig(ConfigBase):
    items: list[dict] = field(
        default_factory=lambda: [
            {
                "title": "Camera_Target",
                "items": [
                    {"type": "double_edit", "title": "X", "action": lambda camera: camera.target.x, "min_val": None, "max_val": None},
                    {"type": "double_edit", "title": "Y", "action": lambda camera: camera.target.y, "min_val": None, "max_val": None},
                    {"type": "double_edit", "title": "Z", "action": lambda camera: camera.target.z, "min_val": None, "max_val": None},
                ],
            },
            {
                "title": "Camera_Position",
                "items": [
                    {"type": "double_edit", "title": "X", "action": lambda camera: camera.position.x, "min_val": None, "max_val": None},
                    {"type": "double_edit", "title": "Y", "action": lambda camera: camera.position.y, "min_val": None, "max_val": None},
                    {"type": "double_edit", "title": "Z", "action": lambda camera: camera.position.z, "min_val": None, "max_val": None},
                ],
            },
        ]
    )


@dataclass
class View3dConfig(ConfigBase):
    viewport: Literal["top", "perspective"] = "perspective"
    background: Color = field(default_factory=lambda: Color.from_hex("#eeeeee"))


# =============================================================================
# =============================================================================
# =============================================================================
# UI
# =============================================================================
# =============================================================================
# =============================================================================


@dataclass
class UIConfig(ConfigBase):
    menubar: MenubarConfig = field(default_factory=MenubarConfig)
    toolbar: ToolbarConfig = field(default_factory=ToolbarConfig)
    statusbar: StatusbarConfig = field(default_factory=StatusbarConfig)
    sidebar: SidebarConfig = field(default_factory=SidebarConfig)
    sidedock: SidedockConfig = field(default_factory=SidedockConfig)
    view3d: View3dConfig = field(default_factory=View3dConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)


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
    vectorsize: float = 0.1
    ui: UIConfig = field(default_factory=UIConfig)
    window: WindowConfig = field(default_factory=WindowConfig)
    renderer: RendererConfig = field(default_factory=RendererConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    cameradialog: CameraDialogConfig = field(default_factory=CameraDialogConfig)
    commands: list[Command] = field(
        default_factory=lambda: [
            camera_settings_cmd,
            change_rendermode_cmd,
            change_view_cmd,
            clear_scene_cmd,
            deselect_all_cmd,
            load_scene_cmd,
            pan_view_cmd,
            rotate_view_cmd,
            save_scene_cmd,
            select_all_cmd,
            select_object_cmd,
            select_window_cmd,
            toggle_sidebar_cmd,
            toggle_sidedock_cmd,
            toggle_statusbar_cmd,
            toggle_toolbar_cmd,
            zoom_selected_cmd,
            zoom_view_cmd,
            obj_settings_cmd,
        ]
    )
