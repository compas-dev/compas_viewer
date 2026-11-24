from collections.abc import Callable
from typing import Any
from typing import TypedDict


class UIItem(TypedDict, total=False):
    """Describe one setup-time menu, toolbar, sidebar, or settings item.

    Viewer shallow-copies supplied sidebar and settings iterables before UI
    construction. Individual definition mappings remain shared with the
    caller and should not be mutated after construction.

    """

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
    tooltip: str
    icon: str
    icon_only: bool


_SIDEBAR_ITEM_TYPES = {"SceneTree", "Sceneform", "AnnotationPanel", "DataPanel", "ObjectSetting", "DatastructureAttributes"}
_SETTINGS_ITEM_TYPES = {"CameraSetting", "DisplaySetting", "GridUnitSetting"}


def _validate_sidebar_items(items: list[UIItem]) -> None:
    """Validate a materialized content-sidebar composition."""
    for item in items:
        itemtype = item.get("type")
        if itemtype in {"SceneTree", "Sceneform"} and item.get("columns") is None:
            raise ValueError("Please setup config for Sceneform")
        if itemtype not in _SIDEBAR_ITEM_TYPES:
            raise ValueError(f"Unsupported sidebar item type: {itemtype!r}.")


def _validate_settings_items(items: list[UIItem]) -> None:
    """Validate a materialized Viewer Settings composition."""
    configured: set[str] = set()
    for item in items:
        itemtype = item.get("type")
        if itemtype is None or itemtype not in _SETTINGS_ITEM_TYPES:
            raise ValueError(f"Unsupported settings item type: {itemtype!r}.")
        if itemtype in configured:
            raise ValueError(f"Duplicate settings item type: {itemtype!r}.")
        configured.add(itemtype)


def default_toolbar_items() -> list[UIItem]:
    """Return the built-in toolbar composition.

    Returns
    -------
    list[UIItem]
        Command-backed view utilities and measurement menu.

    """
    return [
        {"title": "Zoom Selected", "type": "button", "command": "viewer.zoom_selected", "icon": "zoom_selected.svg", "icon_only": True},
        {"title": "Zoom Extents", "type": "button", "command": "viewer.zoom_extents", "icon": "zoom_extents.svg", "icon_only": True},
        {"title": "Capture View", "type": "button", "command": "viewer.capture_view", "icon": "capture_view.svg", "icon_only": True},
        {
            "title": "Measurement",
            "type": "menu_button",
            "icon": "measurement.svg",
            "icon_only": True,
            "items": [
                {"title": "Inspect Distance", "command": "viewer.inspect_distance"},
                {"title": "Add Fixed Distance Dimension", "command": "viewer.add_fixed_distance_dimension"},
                {"title": "Add Associative Distance Dimension", "command": "viewer.add_associative_distance_dimension"},
                {"title": "Cancel Measurement", "command": "viewer.cancel_measurement"},
            ],
        },
    ]


def _geometry_add_items() -> list[UIItem]:
    """Return the fixed geometry hierarchy owned by the Scene menu."""
    return [
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
    ]


def default_menu_items() -> list[UIItem]:
    """Return the built-in menu composition.

    Returns
    -------
    list[UIItem]
        Runtime menu definitions using stable command identifiers.

    """
    return [
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
                {"type": "separator"},
                {"title": "Viewer Settings…", "command": "viewer.show_viewer_settings"},
            ],
        },
        {
            "title": "Edit",
            "items": [
                {"title": "Undo", "command": "viewer.undo"},
                {"title": "Redo", "command": "viewer.redo"},
                {"type": "separator"},
                {"title": "Modify Parameters...", "command": "viewer.modify_selected"},
                {"type": "separator"},
                {"title": "Delete Selected", "command": "viewer.delete_selected", "kwargs": {"source": "menu"}},
            ],
        },
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
            "title": "Measure",
            "items": [
                {"title": "Inspect Distance", "command": "viewer.inspect_distance"},
                {"title": "Inspect Selected Area", "command": "viewer.inspect_selected_area"},
                {"title": "Inspect Selected Volume", "command": "viewer.inspect_selected_volume"},
                {"type": "separator"},
                {"title": "Add Fixed Distance Dimension", "command": "viewer.add_fixed_distance_dimension"},
                {"title": "Add Associative Distance Dimension", "command": "viewer.add_associative_distance_dimension"},
                {"type": "separator"},
                {"title": "Cancel Measurement", "command": "viewer.cancel_measurement"},
            ],
        },
        {
            "title": "Scene",
            "items": [
                {"title": "Clear Scene", "command": "viewer.clear_scene"},
                {"type": "separator"},
                {"title": "Load Scene", "command": "viewer.load_scene"},
                {"title": "Save Scene", "command": "viewer.save_scene"},
                {"type": "separator"},
                {"title": "Add", "items": _geometry_add_items()},
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
        Setup-time content-sidebar definitions.

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
        {"type": "DataPanel"},
        {"type": "AnnotationPanel"},
        {"type": "ObjectSetting"},
    ]


def default_settings_items() -> list[UIItem]:
    """Return the built-in Viewer Settings composition.

    Returns
    -------
    list[UIItem]
        Setup-time settings definitions in presentation order.

    """
    return [
        {"type": "CameraSetting"},
        {"type": "DisplaySetting"},
        {"type": "GridUnitSetting"},
    ]


__all__ = ["UIItem", "default_menu_items", "default_settings_items", "default_sidebar_items", "default_toolbar_items"]
