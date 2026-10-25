from collections.abc import Callable
from typing import Any
from typing import TypedDict


class UIItem(TypedDict, total=False):
    """Describe a runtime menu, toolbar, or sidebar item."""

    title: str
    type: str
    command: str
    args: list[Any]
    kwargs: dict[str, Any]
    checked: bool | Callable[[Any], bool]
    selected: int | Callable[[Any], int]
    state: str
    value: Any
    exclusive: bool
    items: list["UIItem"]
    columns: list[dict[str, Any]]


def default_menu_items() -> list[UIItem]:
    """Return the built-in menu composition.

    Returns
    -------
    list[UIItem]
        Runtime menu definitions using stable command identifiers.

    """
    return [
        {
            "title": "Add",
            "items": [
                {
                    "title": "Primitives",
                    "items": [
                        {"title": title, "command": "viewer.add_geometry", "kwargs": {"kind": kind}}
                        for title, kind in (("Point", "point"), ("Line", "line"), ("Frame", "frame"), ("Plane", "plane"))
                    ],
                },
                {
                    "title": "Curves",
                    "items": [
                        {"title": title, "command": "viewer.add_geometry", "kwargs": {"kind": kind}}
                        for title, kind in (("Polyline", "polyline"), ("Polygon", "polygon"), ("Circle", "circle"), ("Ellipse", "ellipse"))
                    ],
                },
                {
                    "title": "Surfaces",
                    "items": [
                        {"title": "Quad Surface", "command": "viewer.add_geometry", "kwargs": {"kind": "quad_surface"}},
                        {"title": "Saddle Surface", "command": "viewer.add_geometry", "kwargs": {"kind": "saddle_surface"}},
                    ],
                },
                {
                    "title": "Shapes",
                    "items": [
                        {"title": title, "command": "viewer.add_geometry", "kwargs": {"kind": kind}}
                        for title, kind in (
                            ("Box", "box"),
                            ("Sphere", "sphere"),
                            ("Cylinder", "cylinder"),
                            ("Cone", "cone"),
                            ("Capsule", "capsule"),
                            ("Torus", "torus"),
                        )
                    ],
                },
            ],
        },
        {
            "title": "View",
            "items": [
                {"title": "Toolbar", "type": "checkbox", "state": "ui.toolbar.show", "command": "viewer.toggle_toolbar"},
                {"title": "Sidebar", "type": "checkbox", "state": "ui.sidebar.show", "command": "viewer.toggle_sidebar"},
                {"title": "Side Dock", "type": "checkbox", "state": "ui.sidedock.show", "command": "viewer.toggle_sidedock"},
                {"title": "Statusbar", "type": "checkbox", "state": "ui.statusbar.show", "command": "viewer.toggle_statusbar"},
                {"type": "separator"},
                {
                    "title": "Appearance",
                    "type": "group",
                    "items": [
                        {"title": title.title(), "command": "viewer.change_appearance", "state": "ui.appearance", "value": title, "kwargs": {"appearance": title}}
                        for title in ("system", "light", "dark")
                    ],
                },
                {"type": "separator"},
                {
                    "title": "Set Render Mode",
                    "type": "group",
                    "items": [
                        {"title": mode.title(), "command": "viewer.change_rendermode", "state": "renderer.rendermode", "value": mode, "kwargs": {"mode": mode}}
                        for mode in ("shaded", "ghosted", "lighted", "wireframe")
                    ],
                },
                {
                    "title": "Set Current View",
                    "type": "group",
                    "items": [
                        {"title": mode.title(), "command": "viewer.change_view", "state": "renderer.view", "value": mode, "kwargs": {"mode": mode}}
                        for mode in ("perspective", "top", "front", "right", "ortho")
                    ],
                },
                {"type": "separator"},
                {"title": "Grid", "type": "checkbox", "state": "renderer.show_grid", "command": "viewer.toggle_grid"},
                {"type": "separator"},
                {"title": "Zoom Extents", "command": "viewer.zoom_extents"},
                {"title": "Zoom Selected", "command": "viewer.zoom_selected"},
                {"title": "Isolate Selected", "command": "viewer.isolate_selected"},
                {"title": "Show All", "command": "viewer.show_all"},
                {"type": "separator"},
                {"title": "Capture View", "command": "viewer.capture_view"},
            ],
        },
        {"title": "Edit", "items": [{"title": "Modify Parameters...", "command": "viewer.modify_selected"}]},
        {
            "title": "Select",
            "items": [
                {"title": "Select All", "command": "viewer.select_all"},
                {"title": "Select Inverted", "command": "viewer.invert_selection"},
                {"type": "separator"},
                {"title": "Select by Type...", "command": "viewer.select_by_type"},
                {"title": "Select by Color...", "command": "viewer.select_by_color"},
                {"title": "Select by Name...", "command": "viewer.select_by_name"},
                {"type": "separator"},
                {"title": "Isolate Selected", "command": "viewer.isolate_selected"},
                {"title": "Show All", "command": "viewer.show_all"},
                {"type": "separator"},
                {"title": "Deselect All", "command": "viewer.deselect_all"},
            ],
        },
        {
            "title": "Scene",
            "items": [
                {"title": "Clear Scene", "command": "viewer.clear_scene"},
                {"type": "separator"},
                {"title": "Load Scene", "command": "viewer.load_scene"},
                {"title": "Save Scene", "command": "viewer.save_scene"},
            ],
        },
        {
            "title": "Help",
            "items": [
                {"title": "Viewer Docs", "command": "viewer.open_url", "kwargs": {"url": "https://compas.dev/compas_viewer"}},
                {"title": "Viewer Github", "command": "viewer.open_url", "kwargs": {"url": "https://github.com/compas-dev/compas_viewer"}},
                {"type": "separator"},
                {"title": "COMPAS Home", "command": "viewer.open_url", "kwargs": {"url": "https://compas.dev/"}},
                {"title": "COMPAS Docs", "command": "viewer.open_url", "kwargs": {"url": "https://compas.dev/compas"}},
                {"title": "COMPAS Github", "command": "viewer.open_url", "kwargs": {"url": "https://github.com/compas-dev/compas"}},
            ],
        },
    ]


def default_sidebar_items() -> list[UIItem]:
    """Return the built-in sidebar composition.

    Returns
    -------
    list[UIItem]
        Runtime sidebar definitions.

    """
    return [
        {
            "type": "SceneTree",
            "columns": [
                {"title": "Name", "type": "label", "text": lambda obj: obj.name},
                {"title": "Type", "type": "label", "text": lambda obj: type(getattr(obj, "item", obj)).__name__},
                {"title": "Show", "type": "checkbox", "checked": lambda obj: obj.show, "action": lambda obj, checked: setattr(obj, "show", checked)},
            ],
        },
        {"type": "ObjectSetting"},
        {"type": "CameraSetting"},
        {"type": "DisplaySetting"},
    ]


__all__ = ["UIItem", "default_menu_items", "default_sidebar_items"]
