"""
UI Definitions with function references and lambdas.

This module contains the actual UI structure definitions that include
function references, lambdas, and other non-serializable elements.
These are separate from the configuration to keep configs clean and serializable.
"""
from typing import TYPE_CHECKING, List, Dict, Any

if TYPE_CHECKING:
    from compas_viewer import Viewer

# These imports will need to be updated based on the actual command locations
try:
    from compas_viewer.commands import (
        camera_settings_cmd,
        capture_view_cmd,
        change_rendermode_cmd,
        change_view_cmd,
        clear_scene_cmd,
        deselect_all_cmd,
        load_scene_cmd,
        obj_settings_cmd,
        save_scene_cmd,
        select_all_cmd,
        toggle_sidebar_cmd,
        toggle_sidedock_cmd,
        toggle_statusbar_cmd,
        toggle_toolbar_cmd,
    )
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QDesktopServices
except ImportError:
    # Handle case where commands are not available
    pass


def get_default_menu_items() -> List[Dict[str, Any]]:
    """Get the default menu structure."""
    return [
        {
            "title": "View",
            "items": [
                {
                    "title": "Toolbar", 
                    "type": "checkbox", 
                    "checked": lambda viewer: viewer.config.ui.toolbar.show, 
                    "action": toggle_toolbar_cmd
                },
                {
                    "title": "Sidebar", 
                    "type": "checkbox", 
                    "checked": lambda viewer: viewer.config.ui.sidebar.show, 
                    "action": toggle_sidebar_cmd
                },
                {
                    "title": "Side Dock", 
                    "type": "checkbox", 
                    "checked": lambda viewer: viewer.config.ui.sidedock.show, 
                    "action": toggle_sidedock_cmd
                },
                {
                    "title": "Statusbar", 
                    "type": "checkbox", 
                    "checked": lambda viewer: viewer.config.ui.statusbar.show, 
                    "action": toggle_statusbar_cmd
                },
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
                        {"title": "Ortho", "action": change_view_cmd, "kwargs": {"mode": "ortho"}},
                    ],
                },
                {"type": "separator"},
                {"title": "Camera Settings", "action": camera_settings_cmd},
                {"title": "Display Settings", "action": lambda: print("Display Settings")},
                {"title": "Capture View", "action": capture_view_cmd},
                {"type": "separator"},
            ],
        },
        {
            "title": "Select",
            "items": [
                {"title": "Select All", "action": select_all_cmd},
                {"title": "Invert Selection", "action": lambda: print("invert selection")},
                {"type": "separator"},
                {"title": "Deselect All", "action": deselect_all_cmd},
            ],
        },
        {
            "title": "Scene",
            "items": [
                {"title": "Clear Scene", "action": clear_scene_cmd},
                {"type": "separator"},
                {"title": "Load Scene", "action": load_scene_cmd},
                {"title": "Save Scene", "action": save_scene_cmd},
            ],
        },
        {
            "title": "Help",
            "items": [
                {
                    "title": "Viewer Docs", 
                    "action": lambda: QDesktopServices.openUrl(QUrl("https://compas.dev/compas_viewer"))
                },
                {
                    "title": "Viewer Github", 
                    "action": lambda: QDesktopServices.openUrl(QUrl("https://github.com/compas-dev/compas_viewer"))
                },
                {"type": "separator"},
                {
                    "title": "COMPAS Home", 
                    "action": lambda: QDesktopServices.openUrl(QUrl("https://compas.dev/"))
                },
                {
                    "title": "COMPAS Docs", 
                    "action": lambda: QDesktopServices.openUrl(QUrl("https://compas.dev/compas"))
                },
                {
                    "title": "COMPAS Github", 
                    "action": lambda: QDesktopServices.openUrl(QUrl("https://github.com/compas-dev/compas"))
                },
            ],
        },
    ]


def get_default_sidebar_items() -> List[Dict[str, Any]]:
    """Get the default sidebar structure."""
    return [
        {
            "type": "Sceneform",
            "columns": [
                {"title": "Name", "type": "label", "text": lambda obj: obj.name},
                {
                    "title": "Show", 
                    "type": "checkbox", 
                    "checked": lambda obj: obj.show, 
                    "action": lambda obj, checked: setattr(obj, "show", checked)
                },
            ],
        },
        {
            "type": "ObjectSetting",
            "items": [
                {"title": "Name", "items": [{"type": "text_edit", "action": lambda obj: obj.name}]},
                {"title": "Point_Color", "items": [{"type": "color_dialog", "attr": "pointcolor"}]},
                {"title": "Line_Color", "items": [{"type": "color_dialog", "attr": "linecolor"}]},
                {"title": "Face_Color", "items": [{"type": "color_dialog", "attr": "facecolor"}]},
                {
                    "title": "Line_Width", 
                    "items": [{
                        "type": "double_edit", 
                        "action": lambda obj: obj.linewidth, 
                        "min_val": 0.0, 
                        "max_val": 10.0
                    }]
                },
                {
                    "title": "Point_Size", 
                    "items": [{
                        "type": "double_edit", 
                        "action": lambda obj: obj.pointsize, 
                        "min_val": 0.0, 
                        "max_val": 10.0
                    }]
                },
                {
                    "title": "Opacity", 
                    "items": [{
                        "type": "double_edit", 
                        "action": lambda obj: obj.opacity, 
                        "min_val": 0.0, 
                        "max_val": 1.0
                    }]
                },
            ],
        },
    ]


def get_default_camera_dialog_settings() -> List[Dict[str, Any]]:
    """Get the default camera dialog settings."""
    return [
        {
            "title": "Camera_Target",
            "items": [
                {
                    "type": "double_edit", 
                    "title": "X", 
                    "action": lambda camera: camera.target.x, 
                    "min_val": None, 
                    "max_val": None
                },
                {
                    "type": "double_edit", 
                    "title": "Y", 
                    "action": lambda camera: camera.target.y, 
                    "min_val": None, 
                    "max_val": None
                },
                {
                    "type": "double_edit", 
                    "title": "Z", 
                    "action": lambda camera: camera.target.z, 
                    "min_val": None, 
                    "max_val": None
                },
            ],
        },
        {
            "title": "Camera_Position",
            "items": [
                {
                    "type": "double_edit", 
                    "title": "X", 
                    "action": lambda camera: camera.position.x, 
                    "min_val": None, 
                    "max_val": None
                },
                {
                    "type": "double_edit", 
                    "title": "Y", 
                    "action": lambda camera: camera.position.y, 
                    "min_val": None, 
                    "max_val": None
                },
                {
                    "type": "double_edit", 
                    "title": "Z", 
                    "action": lambda camera: camera.position.z, 
                    "min_val": None, 
                    "max_val": None
                },
            ],
        },
    ]


def get_default_commands() -> List[Any]:
    """Get the default command list."""
    try:
        return [
            camera_settings_cmd,
            change_rendermode_cmd,
            change_view_cmd,
            clear_scene_cmd,
            deselect_all_cmd,
            load_scene_cmd,
            save_scene_cmd,
            select_all_cmd,
            toggle_sidebar_cmd,
            toggle_sidedock_cmd,
            toggle_statusbar_cmd,
            toggle_toolbar_cmd,
            obj_settings_cmd,
        ]
    except NameError:
        # Commands not available, return empty list
        return [] 