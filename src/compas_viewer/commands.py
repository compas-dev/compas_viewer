from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import cast

import numpy as np
from numpy import array
from numpy import unique
from numpy.linalg import norm
from numpy.typing import NDArray
from PySide6.QtCore import QEvent
from PySide6.QtCore import Qt
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtGui import QMouseEvent
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QInputDialog
from PySide6.QtWidgets import QMessageBox

import compas
from compas.colors import Color
from compas.datastructures import Datastructure
from compas.geometry import Box
from compas.geometry import Capsule
from compas.geometry import Circle
from compas.geometry import Cone
from compas.geometry import Cylinder
from compas.geometry import Ellipse
from compas.geometry import Frame
from compas.geometry import Geometry
from compas.geometry import Line
from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Polygon
from compas.geometry import PolygonalSurface
from compas.geometry import Polyline
from compas.geometry import Sphere
from compas.geometry import Torus
from compas.scene import Scene

if TYPE_CHECKING:
    from compas_viewer import Viewer
    from compas_viewer.scene import ViewerSceneObject


class Command:
    """Bind user-facing metadata and input shortcuts to a viewer callback.

    Parameters
    ----------
    title
        Label shown for the command in the user interface.
    callback
        Function invoked with the active viewer followed by command arguments.
    description
        Optional longer explanation of the command.
    icon
        Optional icon identifier or path.
    keybinding
        Optional keyboard shortcut.
    mousebinding
        Optional mouse shortcut.
    wheelbinding
        Optional wheel shortcut.
    gesturebinding
        Optional gesture shortcut.

    """

    # we should rename the module to "commands.py"

    @property
    def viewer(self) -> "Viewer":
        from compas_viewer import Viewer

        return Viewer()

    def __init__(
        self,
        *,
        title: str,
        callback: Callable[..., object],
        description: str | None = None,
        icon: str | None = None,
        keybinding: str | None = None,
        mousebinding: str | None = None,
        wheelbinding: str | None = None,
        gesturebinding: str | None = None,
    ) -> None:
        self.title = title
        self.callback = callback
        self.description = description
        self.icon = icon
        self.keybinding = keybinding
        self.mousebinding = mousebinding
        self.wheelbinding = wheelbinding
        self.gesturebinding = gesturebinding

    def __call__(self, *args: Any, **kwargs: Any) -> object:
        return self.callback(self.viewer, *args, **kwargs)


# =============================================================================
# Add geometry
# =============================================================================


def create_geometry(kind: str) -> Geometry:
    """Create default geometry for an Add-menu entry.

    Parameters
    ----------
    kind
        Registered geometry preset name.

    Returns
    -------
    Geometry
        Newly constructed COMPAS geometry.

    Raises
    ------
    ValueError
        If the geometry preset is unknown.

    """
    factories: dict[str, Callable[[], Geometry]] = {
        "point": lambda: Point(0, 0, 0),
        "line": lambda: Line((-1, 0, 0), (1, 0, 0)),
        "frame": Frame.worldXY,
        "plane": Plane.worldXY,
        "polyline": lambda: Polyline([(-1, 0, 0), (0, 1, 0), (1, 0, 0)]),
        "polygon": lambda: Polygon([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)]),
        "circle": lambda: Circle(1.0),
        "ellipse": lambda: Ellipse(1.5, 0.75),
        "quad_surface": lambda: PolygonalSurface([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [[0, 1, 2, 3]]),
        "saddle_surface": lambda: PolygonalSurface(
            [(-1, -1, 0), (0, -1, -0.5), (1, -1, 0), (-1, 0, 0.5), (0, 0, 0), (1, 0, 0.5), (-1, 1, 0), (0, 1, -0.5), (1, 1, 0)],
            [[0, 1, 4, 3], [1, 2, 5, 4], [3, 4, 7, 6], [4, 5, 8, 7]],
        ),
        "box": lambda: Box(1.0),
        "sphere": lambda: Sphere(0.5),
        "cylinder": lambda: Cylinder(0.5, 1.0),
        "cone": lambda: Cone(0.5, 1.0),
        "capsule": lambda: Capsule(0.35, 1.0),
        "torus": lambda: Torus(1.0, 0.25),
    }
    try:
        return factories[kind]()
    except KeyError as error:
        raise ValueError(f"Unknown geometry preset: {kind!r}.") from error


def add_geometry(viewer: "Viewer", kind: str, name: str | None = None) -> "ViewerSceneObject":
    """Add default geometry to the scene from a named preset.

    Parameters
    ----------
    viewer
        Viewer receiving the new geometry.
    kind
        Registered geometry preset name.
    name
        Optional scene-object name.

    Returns
    -------
    ViewerSceneObject
        Scene object created for the geometry.

    """
    geometry = create_geometry(kind)
    for obj in cast(list["ViewerSceneObject"], viewer.scene.objects):
        obj.is_selected = False
    sceneobject = cast("ViewerSceneObject", viewer.scene.add(geometry, name=name or kind.replace("_", " ").title(), is_selected=True))
    if viewer.running:
        _zoom_objects(viewer, [sceneobject])
    return sceneobject


add_geometry_cmd = Command(title="Add Geometry", callback=add_geometry)


# =============================================================================
# =============================================================================
# =============================================================================
# View
# =============================================================================
# =============================================================================
# =============================================================================


def toggle_toolbar(viewer: "Viewer") -> None:
    """Toggle the toolbar visibility.

    Parameters
    ----------
    viewer
        Viewer whose toolbar should be toggled.

    """
    viewer.state.toggle("ui.toolbar.show")


toggle_toolbar_cmd = Command(title="Toolbar", callback=toggle_toolbar)


def toggle_sidebar(viewer: "Viewer") -> None:
    """Toggle the sidebar visibility.

    Parameters
    ----------
    viewer
        Viewer whose sidebar should be toggled.

    """
    viewer.state.toggle("ui.sidebar.show")


toggle_sidebar_cmd = Command(title="Sidebar", callback=toggle_sidebar)


def toggle_sidedock(viewer: "Viewer") -> None:
    """Toggle the side-dock visibility.

    Parameters
    ----------
    viewer
        Viewer whose side dock should be toggled.

    """
    viewer.state.toggle("ui.sidedock.show")


toggle_sidedock_cmd = Command(title="Side Dock", callback=toggle_sidedock)


def toggle_statusbar(viewer: "Viewer") -> None:
    """Toggle the status-bar visibility.

    Parameters
    ----------
    viewer
        Viewer whose status bar should be toggled.

    """
    viewer.state.toggle("ui.statusbar.show")


toggle_statusbar_cmd = Command(title="Statusbar", callback=toggle_statusbar)


def change_appearance(viewer: "Viewer", appearance: Literal["system", "light", "dark"]) -> None:
    """Set the application appearance.

    Parameters
    ----------
    viewer
        Viewer whose application palette should be updated.
    appearance
        Requested system, light, or dark appearance.

    """
    viewer.set_appearance(appearance)


change_appearance_cmd = Command(title="Set Appearance", callback=change_appearance)


def open_url(viewer: "Viewer", url: str) -> bool:
    """Open a URL using the system handler.

    Parameters
    ----------
    viewer
        Active viewer. The argument is accepted for command consistency.
    url
        URL to open.

    Returns
    -------
    bool
        Whether Qt accepted the request.

    """
    del viewer
    return QDesktopServices.openUrl(QUrl(url))


open_url_cmd = Command(title="Open URL", callback=open_url)


def change_rendermode(viewer: "Viewer", mode: Literal["shaded", "ghosted", "lighted", "wireframe"]) -> None:
    """Set the renderer display mode.

    Parameters
    ----------
    viewer
        Viewer to update.
    mode
        Render mode to activate.

    """
    viewer.renderer.rendermode = mode
    viewer.renderer.update()


change_rendermode_cmd = Command(title="Set View3D Render Mode", callback=change_rendermode)


def change_view(viewer: "Viewer", mode: Literal["perspective", "top", "front", "right", "ortho"]) -> None:
    """Set the active camera view.

    Parameters
    ----------
    viewer
        Viewer to update.
    mode
        Camera view to activate.

    """
    viewer.renderer.view = mode
    viewer.renderer.update()


change_view_cmd = Command(title="Set View3D View", callback=change_view)


def camera_settings(viewer: "Viewer") -> None:
    """Focus the camera settings in the sidebar when available.

    Parameters
    ----------
    viewer
        Viewer whose camera settings should be focused.

    """
    # Try to focus on the camera settings tab in the sidebar
    if hasattr(viewer.ui, "sidebar") and hasattr(viewer.ui.sidebar, "tabform"):
        tabform = viewer.ui.sidebar.tabform
        if "Camera" in tabform.tabs:
            tabform.set_current_tab("Camera")
            if hasattr(viewer.ui.sidebar, "camera_setting"):
                viewer.ui.sidebar.camera_setting.update()
        else:
            print("Camera settings tab not found in sidebar")
    else:
        print("Camera settings are available in the sidebar")


camera_settings_cmd = Command(title="Camera Settings", callback=camera_settings)


def capture_view(viewer: "Viewer") -> None:
    """Save the current framebuffer to an image selected by the user.

    Parameters
    ----------
    viewer
        Viewer to capture.

    """
    filepath, _ = QFileDialog.getSaveFileName(parent=viewer.ui.window.widget, caption="Save Image", filter="Images (*.png *.jpg)")
    if not filepath:
        return

    viewer.save_image(Path(filepath))


capture_view_cmd = Command(title="Capture View", callback=capture_view)


# -----------------------------------------------------------------------------
# Events (Temp)
# -----------------------------------------------------------------------------


def pan_view(viewer: "Viewer", event: QMouseEvent) -> None:
    """Pan the camera in response to a mouse event.

    Parameters
    ----------
    viewer
        Viewer whose camera should be panned.
    event
        Mouse event controlling the pan gesture.

    """
    etype = event.type()

    if etype == QEvent.Type.MouseButtonPress:
        QApplication.setOverrideCursor(Qt.CursorShape.OpenHandCursor)

    elif etype == QEvent.Type.MouseMove:
        if not viewer.mouse.has_dragged():
            return
        dx = viewer.mouse.dx()
        dy = viewer.mouse.dy()
        viewer.renderer.camera.pan(dx, dy)

    elif etype == QEvent.Type.MouseButtonRelease:
        QApplication.restoreOverrideCursor()

    viewer.renderer.update()


pan_view_cmd = Command(title="Pan View", callback=pan_view, mousebinding="RIGHT + SHIFT")


def rotate_view(viewer: "Viewer", event: QMouseEvent) -> None:
    """Rotate the camera in response to a mouse event.

    Parameters
    ----------
    viewer
        Viewer whose camera should be rotated.
    event
        Mouse event controlling the rotation gesture.

    """
    etype = event.type()

    if etype == QEvent.Type.MouseButtonPress:
        QApplication.setOverrideCursor(Qt.CursorShape.SizeAllCursor)

    elif etype == QEvent.Type.MouseMove:
        if not viewer.mouse.has_dragged():
            return
        dx = viewer.mouse.dx()
        dy = viewer.mouse.dy()
        viewer.renderer.camera.rotate(dx, dy)

    elif etype == QEvent.Type.MouseButtonRelease:
        QApplication.restoreOverrideCursor()

    viewer.renderer.update()


rotate_view_cmd = Command(title="Rotate View", callback=rotate_view, mousebinding="RIGHT")


def zoom_selected(viewer: "Viewer") -> None:
    """Frame the selected objects.

    Parameters
    ----------
    viewer
        Viewer whose camera should be updated.

    """
    objects = cast(list["ViewerSceneObject"], viewer.scene.objects)
    _zoom_objects(viewer, [obj for obj in objects if obj.is_selected])


def _zoom_objects(viewer: "Viewer", objects: list["ViewerSceneObject"]) -> bool:
    """Frame the bounding boxes of a collection of scene objects."""
    selected_objs = [obj for obj in objects if obj.show]
    extents = []

    for obj in selected_objs:
        if obj.bounding_box is not None:
            obj._update_bounding_box()
            extents.append(obj.bounding_box)

    extents = array([obj.bounding_box for obj in selected_objs if obj.bounding_box is not None])

    if len(extents) == 0:
        return False

    extents = extents.reshape(-1, 3)
    max_corner = extents.max(axis=0)
    min_corner = extents.min(axis=0)
    extent = float(norm(max_corner - min_corner))
    if extent > 0:
        viewer.renderer.camera.scale = extent / 10  # 10 is a tuned framing factor.
    elif viewer.renderer.camera.scale <= 0:
        viewer.renderer.camera.scale = 1.0
    center = (max_corner + min_corner) / 2
    distance = max(extent, 1)

    viewer.renderer.camera.target = cast(list[float], center)
    direction = viewer.renderer.camera.target - viewer.renderer.camera.position
    vec = direction / direction.length
    viewer.renderer.camera.position = cast(list[float], viewer.renderer.camera.target - vec * distance)

    viewer.renderer.update()
    return True


zoom_selected_cmd = Command(title="Zoom Selected", callback=zoom_selected, keybinding="F")


def zoom_extents(viewer: "Viewer") -> None:
    """Frame all visible objects in the scene.

    Parameters
    ----------
    viewer
        Viewer whose visible scene extents should be framed.

    """
    objects = cast(list["ViewerSceneObject"], viewer.scene.objects)
    _zoom_objects(viewer, objects)


zoom_extents_cmd = Command(title="Zoom Extents", callback=zoom_extents, keybinding="H")


def isolate_selected(viewer: "Viewer") -> None:
    """Show selected objects and their ancestors, hide all others, and frame them.

    Parameters
    ----------
    viewer
        Viewer containing the selection to isolate.

    """
    objects = cast(list["ViewerSceneObject"], viewer.scene.objects)
    selected = [obj for obj in objects if obj.is_selected]
    if not selected:
        return

    visible = set(selected)
    for obj in selected:
        parent = obj.parent
        while parent is not None and not getattr(parent, "is_root", False):
            visible.add(cast("ViewerSceneObject", parent))
            parent = parent.parent

    for obj in objects:
        obj.show = obj in visible

    viewer.ui.sidebar.update()
    viewer.renderer.update()
    _zoom_objects(viewer, selected)


isolate_selected_cmd = Command(title="Isolate Selected", callback=isolate_selected)


def show_all(viewer: "Viewer") -> None:
    """Show every object in the scene.

    Parameters
    ----------
    viewer
        Viewer whose scene objects should be made visible.

    """
    for obj in cast(list["ViewerSceneObject"], viewer.scene.objects):
        obj.show = True

    viewer.ui.sidebar.update()
    viewer.renderer.update()


show_all_cmd = Command(title="Show All", callback=show_all)


def toggle_grid(viewer: "Viewer") -> None:
    """Toggle display of the ground grid.

    Parameters
    ----------
    viewer
        Viewer whose grid visibility should be toggled.

    """
    viewer.state.toggle("renderer.show_grid")


toggle_grid_cmd = Command(title="Grid", callback=toggle_grid)


def zoom_view(viewer: "Viewer", event: QWheelEvent) -> None:
    """Zoom the camera in response to a wheel event.

    Parameters
    ----------
    viewer
        Viewer whose camera should be zoomed.
    event
        Wheel event determining the zoom amount.

    """
    degrees = event.angleDelta().y() / 8
    steps = degrees / 15
    viewer.renderer.camera.zoom(steps)
    viewer.renderer.update()


zoom_view_cmd = Command(title="Zoom View", callback=zoom_view, wheelbinding="")


# =============================================================================
# =============================================================================
# =============================================================================
# Select
# =============================================================================
# =============================================================================
# =============================================================================


def select_all(viewer: "Viewer") -> None:
    """Select every visible scene object.

    Parameters
    ----------
    viewer
        Viewer containing the objects to select.

    """
    for obj in cast(list["ViewerSceneObject"], viewer.scene.objects):
        if obj.show:
            obj.is_selected = True

    viewer.ui.sidebar.update()
    viewer.renderer.update()


select_all_cmd = Command(title="Select All", callback=select_all)


def invert_selection(viewer: "Viewer") -> None:
    """Invert the selection state of every visible scene object.

    Parameters
    ----------
    viewer
        Viewer containing the objects whose selection should be inverted.

    """
    for obj in cast(list["ViewerSceneObject"], viewer.scene.objects):
        if obj.show:
            obj.is_selected = not obj.is_selected

    viewer.ui.sidebar.update()
    viewer.renderer.update()


invert_selection_cmd = Command(title="Select Inverted", callback=invert_selection)


def deselect_all(viewer: "Viewer") -> None:
    """Clear the current scene selection.

    Parameters
    ----------
    viewer
        Viewer whose selection should be cleared.

    """
    for obj in cast(list["ViewerSceneObject"], viewer.scene.objects):
        obj.is_selected = False

    viewer.ui.sidebar.update()
    viewer.renderer.update()


deselect_all_cmd = Command(title="Deselect All", callback=deselect_all, keybinding="Escape")


def _select_matching(viewer: "Viewer", predicate: Callable[["ViewerSceneObject"], bool]) -> None:
    """Replace the selection with objects matching a predicate."""
    for obj in cast(list["ViewerSceneObject"], viewer.scene.objects):
        obj.is_selected = predicate(obj)
    viewer.ui.sidebar.update()
    viewer.renderer.update()


def select_by_type(viewer: "Viewer", type_name: str | type | None = None) -> None:
    """Select objects by scene-object or underlying item type.

    Parameters
    ----------
    viewer
        Viewer containing the objects to filter.
    type_name
        Type or case-insensitive class name. A chooser is shown when omitted.

    """
    objects = cast(list["ViewerSceneObject"], viewer.scene.objects)
    if type_name is None:
        names = sorted({type(obj).__name__ for obj in objects} | {type(obj.item).__name__ for obj in objects if getattr(obj, "item", None) is not None})
        if not names:
            return
        type_name, accepted = QInputDialog.getItem(viewer.ui.window.widget, "Select by Type", "Object type", names, editable=False)
        if not accepted or type_name is None:
            return

    if isinstance(type_name, type):

        def predicate(obj: "ViewerSceneObject") -> bool:
            return isinstance(obj, type_name) or isinstance(getattr(obj, "item", None), type_name)

    else:
        normalized = type_name.casefold()

        def predicate(obj: "ViewerSceneObject") -> bool:
            return type(obj).__name__.casefold() == normalized or type(getattr(obj, "item", None)).__name__.casefold() == normalized

    _select_matching(viewer, predicate)


select_by_type_cmd = Command(title="Select by Type...", callback=select_by_type)


def select_by_name(viewer: "Viewer", name: str | None = None) -> None:
    """Select objects whose names contain a case-insensitive search term.

    Parameters
    ----------
    viewer
        Viewer containing the objects to filter.
    name
        Name fragment. A text prompt is shown when omitted.

    """
    if name is None:
        name, accepted = QInputDialog.getText(viewer.ui.window.widget, "Select by Name", "Name contains")
        if not accepted or name is None:
            return
    normalized = name.casefold()
    _select_matching(viewer, lambda obj: normalized in str(getattr(obj, "name", "")).casefold())


select_by_name_cmd = Command(title="Select by Name...", callback=select_by_name)


def select_by_color(viewer: "Viewer", color: Color | str | None = None) -> None:
    """Select objects using any matching display color.

    Parameters
    ----------
    viewer
        Viewer containing the objects to filter.
    color
        COMPAS color or hexadecimal color string. A prompt is shown when omitted.

    """
    if color is None:
        value, accepted = QInputDialog.getText(viewer.ui.window.widget, "Select by Color", "Hex color", text="#ffffff")
        if not accepted:
            return
        color = value
    target = Color.from_hex(color) if isinstance(color, str) else color
    if target is None:
        return

    def matches(obj: "ViewerSceneObject") -> bool:
        for name in ("color", "pointcolor", "linecolor", "facecolor", "surfacecolor"):
            value = getattr(obj, name, None)
            if isinstance(value, Color) and value.rgba == target.rgba:
                return True
        return False

    _select_matching(viewer, matches)


select_by_color_cmd = Command(title="Select by Color...", callback=select_by_color)


# -----------------------------------------------------------------------------
# Events (Temp)
# -----------------------------------------------------------------------------


def select_object(viewer: "Viewer", event: QMouseEvent) -> None:
    """Select the scene object under the mouse pointer.

    Parameters
    ----------
    viewer
        Viewer containing the object to select.
    event
        Mouse event identifying the screen position.

    """
    etype = event.type()

    if etype == QEvent.Type.MouseButtonPress:
        for _, obj in viewer.scene.instance_colors.items():
            obj.is_selected = False

        x = viewer.mouse.last_pos.x()
        y = viewer.mouse.last_pos.y()
        instance_color = viewer.renderer.read_instance_color((x, y, x, y))
        selected_obj = _object_from_instance_colors(viewer, instance_color)
        if selected_obj:
            selected_obj.is_selected = True

        viewer.ui.sidebar.update()

    viewer.renderer.update()


select_object_cmd = Command(title="Select Object", callback=select_object, mousebinding="LEFT")


def _object_from_instance_colors(viewer: "Viewer", pixels: NDArray[np.uint8]) -> "ViewerSceneObject | None":
    """Resolve the most frequently sampled registered instance color."""
    colors, counts = unique(pixels, axis=0, return_counts=True)
    candidates = [(int(count), viewer.scene.instance_colors.get((int(color[0]), int(color[1]), int(color[2])))) for color, count in zip(colors, counts, strict=True)]
    return max((candidate for candidate in candidates if candidate[1] is not None), default=(0, None), key=lambda candidate: candidate[0])[1]


def _window_instance_colors(
    viewer: "Viewer",
    inside_pixels: NDArray[np.uint8],
    all_pixels: NDArray[np.uint8] | None = None,
) -> set[tuple[int, int, int]]:
    """Resolve crossing or fully-contained colors from instance-map pixels."""
    inside_colors, inside_counts = unique(inside_pixels, axis=0, return_counts=True)
    inside = {
        (int(color[0]), int(color[1]), int(color[2])): int(count)
        for color, count in zip(inside_colors, inside_counts, strict=True)
        if (int(color[0]), int(color[1]), int(color[2])) in viewer.scene.instance_colors
    }
    if all_pixels is None:
        return set(inside)

    all_colors, all_counts = unique(all_pixels, axis=0, return_counts=True)
    totals = {(int(color[0]), int(color[1]), int(color[2])): int(count) for color, count in zip(all_colors, all_counts, strict=True)}
    return {color for color, count in inside.items() if count == totals.get(color)}


def select_multiple(viewer: "Viewer", event: QMouseEvent) -> None:
    """Add the scene object under the pointer to the selection.

    Parameters
    ----------
    viewer
        Viewer containing the object to select.
    event
        Mouse event identifying the screen position.

    """
    etype = event.type()

    if etype == QEvent.Type.MouseButtonPress:
        x = viewer.mouse.last_pos.x()
        y = viewer.mouse.last_pos.y()
        instance_color = viewer.renderer.read_instance_color((x, y, x, y))
        selected_obj = _object_from_instance_colors(viewer, instance_color)
        if selected_obj:
            selected_obj.is_selected = True
            viewer.ui.sidebar.update()

    viewer.renderer.update()


select_multiple_cmd = Command(title="Add to Selection", callback=select_multiple, mousebinding="LEFT + CTRL")


def select_window(viewer: "Viewer", event: QMouseEvent) -> None:
    """Update a directional rectangular selection gesture.

    Left-to-right windows select only objects whose visible rendered footprint
    is fully contained. Right-to-left windows select every intersected object.

    Parameters
    ----------
    viewer
        Viewer containing the objects to select.
    event
        Mouse event controlling the selection rectangle.

    """
    etype = event.type()

    if etype == QEvent.Type.MouseButtonPress:
        viewer.mouse.window_start_point = event.pos()

    elif etype == QEvent.Type.MouseMove:
        viewer.mouse.is_tracing_a_window = True  # this results in the drawing of the selection window
        if not viewer.mouse.window_start_point:
            viewer.mouse.window_start_point = event.pos()

    elif etype == QEvent.Type.MouseButtonRelease:
        viewer.mouse.is_tracing_a_window = False  # this stops the drawing of the selection window
        viewer.mouse.window_end_point = event.pos()

        start = viewer.mouse.window_start_point
        end = viewer.mouse.window_end_point
        assert start is not None and end is not None

        # ignore small windows
        if abs(start.x() - end.x()) * abs(start.y() - end.y()) <= 4:
            return

        # Deselect all objects first
        for _, obj in viewer.scene.instance_colors.items():
            obj.is_selected = False

        box = (start.x(), start.y(), end.x(), end.y())
        fully_contained = end.x() >= start.x()
        if fully_contained:
            instance_color, all_instance_colors = viewer.renderer.read_instance_colors([box, (0, 0, viewer.renderer.width(), viewer.renderer.height())])
        else:
            instance_color = viewer.renderer.read_instance_color(box)
            all_instance_colors = None
        selected_colors = _window_instance_colors(viewer, instance_color, all_instance_colors)

        # Select based on instance colors
        for color, obj in viewer.scene.instance_colors.items():
            if color in selected_colors:
                obj.is_selected = True

        viewer.ui.sidebar.update()

    viewer.renderer.update()


select_window_cmd = Command(title="Select Box", callback=select_window, mousebinding="LEFT + SHIFT")


def deselect_object(viewer: "Viewer", event: QMouseEvent) -> None:
    """Deselect the scene object under the mouse pointer.

    Parameters
    ----------
    viewer
        Viewer containing the object to deselect.
    event
        Mouse event identifying the screen position.

    """
    etype = event.type()

    if etype == QEvent.Type.MouseButtonPress:
        x = viewer.mouse.last_pos.x()
        y = viewer.mouse.last_pos.y()
        instance_color = viewer.renderer.read_instance_color((x, y, x, y))
        selected_obj = _object_from_instance_colors(viewer, instance_color)
        if selected_obj:
            selected_obj.is_selected = False

        viewer.ui.sidebar.update()

    viewer.renderer.update()


deselect_object_cmd = Command(title="Deselect Object", callback=deselect_object, mousebinding="LEFT")


def deselect_window() -> None:
    """Provide a placeholder for rectangular deselection."""
    pass


# =============================================================================
# =============================================================================
# =============================================================================
# Selections
# =============================================================================
# =============================================================================
# =============================================================================


def modify_selected(viewer: "Viewer") -> bool:
    """Edit parameters of the data object behind one selected scene object.

    Parameters
    ----------
    viewer
        Viewer containing the selected object.

    Returns
    -------
    bool
        ``True`` if parameter changes were applied; otherwise ``False``.

    """
    from compas_viewer.components import ParameterForm
    from compas_viewer.scene import modify_object_parameters

    selected = [obj for obj in cast(list["ViewerSceneObject"], viewer.scene.objects) if obj.is_selected]
    parent = viewer.ui.window.widget
    if len(selected) != 1:
        QMessageBox.information(parent, "Modify Parameters", "Select exactly one object to modify.")
        return False

    sceneobject = selected[0]
    data = sceneobject.data
    if data is None:
        QMessageBox.information(parent, "Modify Parameters", "The selected scene object has no underlying data object.")
        return False

    dialog = ParameterForm(data, title=f"Modify {sceneobject.name}", parent=parent)
    if dialog.exec() != dialog.DialogCode.Accepted:
        return False

    values = dialog.values()
    if not values:
        QMessageBox.information(parent, "Modify Parameters", "This object has no editable scalar parameters.")
        return False

    try:
        modify_object_parameters(data, values)
    except Exception as error:
        QMessageBox.critical(parent, "Could Not Modify Object", str(error))
        return False

    sceneobject.refresh_data()
    if viewer.running:
        viewer.renderer.rebuild_buffers()
        viewer.renderer.update()
    viewer.ui.sidebar.update()
    return True


modify_selected_cmd = Command(title="Modify Parameters...", callback=modify_selected)


# =============================================================================


def delete_selected(viewer: "Viewer") -> None:
    """Remove all selected objects from the scene.

    Parameters
    ----------
    viewer
        Viewer containing the objects to remove.

    """
    for obj in cast(list["ViewerSceneObject"], viewer.scene.objects):
        if obj.is_selected:
            viewer.scene.remove(obj)
            del obj
    viewer.renderer.update()


delete_selected_cmd = Command(title="Delete Selected", callback=delete_selected, keybinding="Delete")


# =============================================================================
# =============================================================================
# =============================================================================
# Scene
# =============================================================================
# =============================================================================
# =============================================================================


def clear_scene(viewer: "Viewer") -> None:
    """Remove every object from the scene and refresh the viewer.

    Parameters
    ----------
    viewer
        Viewer whose scene should be cleared.

    """
    for obj in cast(list["ViewerSceneObject"], viewer.scene.objects):
        viewer.scene.remove(obj, rebuild_buffers=False)
        del obj

    viewer.renderer.rebuild_buffers()
    viewer.renderer.update()
    viewer.ui.sidebar.update()


clear_scene_cmd = Command(title="Clear Scene", callback=clear_scene)


def load_from_file(viewer: "Viewer", filepath: str | Path) -> bool:
    """Load a scene or geometries from a JSON file.

    Parameters
    ----------
    viewer
        The viewer instance.
    filepath
        Path to the JSON file containing the scene.

    Returns
    -------
    bool
        `True` if supported data was loaded; otherwise `False`.

    """
    try:
        obj = compas.json_load(Path(filepath))
        if isinstance(obj, Scene):
            clear_scene(viewer)
            viewer.scene = obj
            viewer.renderer.rebuild_buffers()
            viewer.renderer.update()
            viewer.ui.sidebar.update()
        elif isinstance(obj, (Geometry, Datastructure)):
            viewer.scene.add(obj)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (Geometry, Datastructure)):
                    viewer.scene.add(item)
        else:
            raise ValueError(f"Unsupported object type: {type(obj)}")

        return True
    except Exception as error:
        print(f"Error loading: {error}")
        return False


def load_scene(viewer: "Viewer") -> None:
    """Load a scene or geometry from a user-selected JSON file.

    Parameters
    ----------
    viewer
        Viewer into which the selected file should be loaded.

    """
    filepath, _ = QFileDialog.getOpenFileName(parent=viewer.ui.window.widget, filter="JSON files (*.json)")
    if not filepath:
        return

    load_from_file(viewer, Path(filepath))


load_scene_cmd = Command(title="Load Scene", callback=load_scene)


def save_scene(viewer: "Viewer") -> None:
    """Save the scene to a user-selected JSON file.

    Parameters
    ----------
    viewer
        Viewer whose scene should be saved.

    """
    filepath, _ = QFileDialog.getSaveFileName(parent=viewer.ui.window.widget, filter="JSON files (*.json)")
    if not filepath:
        return

    compas.json_dump(viewer.scene, Path(filepath))


save_scene_cmd = Command(title="Save Scene", callback=save_scene)


# =============================================================================
# =============================================================================
# =============================================================================
# Data
# =============================================================================
# =============================================================================
# =============================================================================


def load_data() -> None:
    """Provide a placeholder for loading arbitrary viewer data."""
    pass


load_data_cmd = Command(title="Load Data", callback=lambda: print("load data"))


def builtin_commands() -> dict[str, Command]:
    """Return the built-in commands keyed by stable identifier.

    Returns
    -------
    dict[str, Command]
        Fresh command mapping for a viewer registry.

    """
    return {
        "viewer.add_geometry": add_geometry_cmd,
        "viewer.capture_view": capture_view_cmd,
        "viewer.change_appearance": change_appearance_cmd,
        "viewer.change_rendermode": change_rendermode_cmd,
        "viewer.change_view": change_view_cmd,
        "viewer.clear_scene": clear_scene_cmd,
        "viewer.delete_selected": delete_selected_cmd,
        "viewer.deselect_all": deselect_all_cmd,
        "viewer.invert_selection": invert_selection_cmd,
        "viewer.isolate_selected": isolate_selected_cmd,
        "viewer.load_scene": load_scene_cmd,
        "viewer.modify_selected": modify_selected_cmd,
        "viewer.open_url": open_url_cmd,
        "viewer.pan_view": pan_view_cmd,
        "viewer.rotate_view": rotate_view_cmd,
        "viewer.save_scene": save_scene_cmd,
        "viewer.select_all": select_all_cmd,
        "viewer.select_by_color": select_by_color_cmd,
        "viewer.select_by_name": select_by_name_cmd,
        "viewer.select_by_type": select_by_type_cmd,
        "viewer.select_multiple": select_multiple_cmd,
        "viewer.select_object": select_object_cmd,
        "viewer.select_window": select_window_cmd,
        "viewer.show_all": show_all_cmd,
        "viewer.toggle_grid": toggle_grid_cmd,
        "viewer.toggle_sidebar": toggle_sidebar_cmd,
        "viewer.toggle_sidedock": toggle_sidedock_cmd,
        "viewer.toggle_statusbar": toggle_statusbar_cmd,
        "viewer.toggle_toolbar": toggle_toolbar_cmd,
        "viewer.zoom_extents": zoom_extents_cmd,
        "viewer.zoom_selected": zoom_selected_cmd,
        "viewer.zoom_view": zoom_view_cmd,
    }
