import pathlib
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Literal
from typing import Optional

from numpy import all
from numpy import any
from numpy import array
from numpy import unique
from numpy.linalg import norm
from PySide6.QtCore import QEvent
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QFileDialog

import compas
from compas.scene import Scene
from compas_viewer.components.camerasetting import CameraSettingsDialog
from compas_viewer.components.objectsetting import ObjectSettingDialog

if TYPE_CHECKING:
    from compas_viewer import Viewer


class Command:
    # we should rename the module to "commands.py"

    @property
    def viewer(self):
        from compas_viewer import Viewer

        return Viewer()

    def __init__(
        self,
        *,
        title: str,
        callback: Callable,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        keybinding: Optional[str] = None,
        mousebinding: Optional[str] = None,
        wheelbinding: Optional[str] = None,
        gesturebinding: Optional[str] = None,
    ):
        self.title = title
        self.callback = callback
        self.description = description
        self.icon = icon
        self.keybinding = keybinding
        self.mousebinding = mousebinding
        self.wheelbinding = wheelbinding
        self.gesturebinding = gesturebinding

    def __call__(self, *args: Any, **kwargs: Any) -> Callable:
        return self.callback(self.viewer, *args, **kwargs)


# =============================================================================
# =============================================================================
# =============================================================================
# View
# =============================================================================
# =============================================================================
# =============================================================================


def toggle_toolbar(viewer: "Viewer"):
    viewer.ui.toolbar.widget.setVisible(not viewer.ui.toolbar.widget.isVisible())


toggle_toolbar_cmd = Command(title="Toolbar", callback=toggle_toolbar)


def toggle_sidebar(viewer: "Viewer"):
    viewer.ui.sidebar.widget.setVisible(not viewer.ui.sidebar.widget.isVisible())


toggle_sidebar_cmd = Command(title="Sidebar", callback=toggle_sidebar)


def toggle_sidedock(viewer: "Viewer"):
    viewer.ui.sidedock.widget.setVisible(not viewer.ui.sidedock.widget.isVisible())


toggle_sidedock_cmd = Command(title="Side Dock", callback=toggle_sidedock)


def toggle_statusbar(viewer: "Viewer"):
    viewer.ui.statusbar.widget.setVisible(not viewer.ui.statusbar.widget.isVisible())


toggle_statusbar_cmd = Command(title="Statusbar", callback=toggle_statusbar)


def change_rendermode(viewer: "Viewer", mode: Literal["Shaded", "Ghosted", "Lighted", "Wireframe"]):
    viewer.renderer.rendermode = mode.lower()
    viewer.renderer.update()


change_rendermode_cmd = Command(title="Set View3D Render Mode", callback=change_rendermode)


def change_view(viewer: "Viewer", mode: Literal["Perspective", "Top", "Front", "Right"]):
    viewer.renderer.view = mode.lower()
    viewer.renderer.update()


change_view_cmd = Command(title="Set View3D View", callback=change_view)


def camera_settings(viewer: "Viewer"):
    CameraSettingsDialog().exec()


camera_settings_cmd = Command(title="Camera Settings", callback=camera_settings)


def capture_view(viewer: "Viewer"):
    result = QFileDialog.getSaveFileName(parent=viewer.ui.window.widget, caption="Save Image", filter="Images (*.png *.jpg)")
    if not result:
        return

    filepath = pathlib.Path(result[0])

    qimage = viewer.renderer.grabFramebuffer()
    qimage.save(str(filepath), filepath.suffix[1:])


capture_view_cmd = Command(title="Capture View", callback=capture_view)


# -----------------------------------------------------------------------------
# Events (Temp)
# -----------------------------------------------------------------------------


def pan_view(viewer: "Viewer", event: QMouseEvent):
    etype = event.type()

    if etype == QEvent.Type.MouseButtonPress:
        QApplication.setOverrideCursor(Qt.CursorShape.OpenHandCursor)

    elif etype == QEvent.Type.MouseMove:
        dx = viewer.mouse.dx()
        dy = viewer.mouse.dy()
        viewer.renderer.camera.pan(dx, dy)

    elif etype == QEvent.Type.MouseButtonRelease:
        QApplication.restoreOverrideCursor()

    viewer.renderer.update()


pan_view_cmd = Command(title="Pan View", callback=pan_view, mousebinding="RIGHT + SHIFT")


def rotate_view(viewer: "Viewer", event: QMouseEvent):
    etype = event.type()

    if etype == QEvent.Type.MouseButtonPress:
        QApplication.setOverrideCursor(Qt.CursorShape.SizeAllCursor)

    elif etype == QEvent.Type.MouseMove:
        dx = viewer.mouse.dx()
        dy = viewer.mouse.dy()
        viewer.renderer.camera.rotate(dx, dy)

    elif etype == QEvent.Type.MouseButtonRelease:
        QApplication.restoreOverrideCursor()

    viewer.renderer.update()


rotate_view_cmd = Command(title="Rotate View", callback=rotate_view, mousebinding="RIGHT")


def zoom_selected(viewer: "Viewer"):
    selected_objs = [obj for obj in viewer.scene.objects if obj.is_selected]
    if len(selected_objs) == 0:
        selected_objs = viewer.scene.objects
    extents = []

    for obj in selected_objs:
        if obj.bounding_box is not None:
            obj._update_bounding_box()
            extents.append(obj.bounding_box)

    extents = array([obj.bounding_box for obj in selected_objs if obj.bounding_box is not None])

    if len(extents) == 0:
        return

    extents = extents.reshape(-1, 3)
    max_corner = extents.max(axis=0)
    min_corner = extents.min(axis=0)
    viewer.renderer.camera.scale = float((norm(max_corner - min_corner)) / 10)  # 10 is a tuned magic number
    center = (max_corner + min_corner) / 2
    distance = max(norm(max_corner - min_corner), 1)

    viewer.renderer.camera.target = center
    vec = (viewer.renderer.camera.target - viewer.renderer.camera.position) / norm(viewer.renderer.camera.target - viewer.renderer.camera.position)
    viewer.renderer.camera.position = viewer.renderer.camera.target - vec * distance

    viewer.renderer.update()


zoom_selected_cmd = Command(title="Zoom Selected", callback=zoom_selected, keybinding="F")


def zoom_view(viewer: "Viewer", event: QWheelEvent):
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


def select_all(viewer: "Viewer"):
    for obj in viewer.scene.objects:
        if obj.show and not obj.is_locked:
            obj.is_selected = True

    viewer.ui.sidebar.update()
    viewer.renderer.update()


select_all_cmd = Command(title="Select All", callback=select_all)


def deselect_all(viewer: "Viewer"):
    for obj in viewer.scene.objects:
        obj.is_selected = False

    viewer.ui.sidebar.update()
    viewer.renderer.update()


deselect_all_cmd = Command(title="DeSelect All", callback=deselect_all)


# -----------------------------------------------------------------------------
# Events (Temp)
# -----------------------------------------------------------------------------


def select_object(viewer: "Viewer", event: QMouseEvent):
    etype = event.type()

    if etype == QEvent.Type.MouseButtonPress:
        for _, obj in viewer.scene.instance_colors.items():
            obj.is_selected = False

        x = viewer.mouse.last_pos.x()
        y = viewer.mouse.last_pos.y()
        instance_color = viewer.renderer.read_instance_color((x, y, x, y))
        unique_color = unique(instance_color, axis=0, return_counts=False)

        selected_obj = viewer.scene.instance_colors.get(tuple(unique_color[0]))  # type: ignore
        if selected_obj:
            selected_obj.is_selected = True

        viewer.ui.sidebar.update()

    viewer.renderer.update()


select_object_cmd = Command(title="Select Object", callback=select_object, mousebinding="LEFT")


def select_multiple(viewer: "Viewer", event: QMouseEvent):
    etype = event.type()

    if etype == QEvent.Type.MouseButtonPress:
        x = viewer.mouse.last_pos.x()
        y = viewer.mouse.last_pos.y()
        instance_color = viewer.renderer.read_instance_color((x, y, x, y))
        unique_color = unique(instance_color, axis=0, return_counts=False)

        selected_obj = viewer.scene.instance_colors.get(tuple(unique_color[0]))  # type: ignore
        if selected_obj:
            selected_obj.is_selected = True
            viewer.ui.sidebar.update()

    viewer.renderer.update()


select_multiple_cmd = Command(title="Select Multiple", callback=select_multiple, mousebinding="LEFT")


def select_window(viewer: "Viewer", event: QMouseEvent):
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

        # ignore small windows
        if abs(start.x() - end.x()) * abs(start.y() - end.y()) <= 4:
            return

        # Deselect all objects first
        for _, obj in viewer.scene.instance_colors.items():
            obj.is_selected = False

        # Identify unique instance colors
        instance_color = viewer.renderer.read_instance_color((start.x(), start.y(), end.x(), end.y()))
        unique_colors_set = set(map(tuple, instance_color))
        unique_colors = array(list(unique_colors_set))

        if len(unique_colors) == 0:
            return

        # Select based on instance colors
        for color, obj in viewer.scene.instance_colors.items():
            if any(all(color == unique_colors, axis=1)):
                obj.is_selected = True
                continue

        viewer.ui.sidebar.update()

    viewer.renderer.update()


select_window_cmd = Command(title="Select Box", callback=select_window, mousebinding="LEFT + SHIFT")


def deselect_object(viewer: "Viewer", event: QMouseEvent):
    etype = event.type()

    if etype == QEvent.Type.MouseButtonPress:
        x = viewer.mouse.last_pos.x()
        y = viewer.mouse.last_pos.y()
        instance_color = viewer.renderer.read_instance_color((x, y, x, y))
        unique_color = unique(instance_color, axis=0, return_counts=False)

        selected_obj = viewer.scene.instance_colors.get(tuple(unique_color[0]))  # type: ignore
        if selected_obj:
            selected_obj.is_selected = False

        viewer.ui.sidebar.update()

    viewer.renderer.update()


deselect_object_cmd = Command(title="Deselect Object", callback=deselect_object, mousebinding="LEFT")


def deselect_window():
    pass


# =============================================================================
# =============================================================================
# =============================================================================
# Selections
# =============================================================================
# =============================================================================
# =============================================================================


def delete_selected():
    from compas_viewer import Viewer

    viewer = Viewer()

    for obj in viewer.scene.objects:
        if obj.is_selected:
            viewer.scene.remove(obj)
            del obj
    viewer.renderer.update()


# =============================================================================
# =============================================================================
# =============================================================================
# Scene
# =============================================================================
# =============================================================================
# =============================================================================


def clear_scene(viewer: "Viewer"):
    for obj in viewer.scene.objects:
        viewer.scene.remove(obj)
        del obj

    viewer.ui.sidebar.update()
    viewer.renderer.update()


clear_scene_cmd = Command(title="Clear Scene", callback=clear_scene)


def load_scene(viewer: "Viewer"):
    result = QFileDialog.getOpenFileName(parent=viewer.ui.window.widget, filter="JSON files (*.json)")
    if not result:
        return

    scene = compas.json_load(result[0])
    if not isinstance(scene, Scene):
        print("No scene found in this file.")

    clear_scene(viewer)

    viewer.scene = scene
    viewer.renderer.update()


load_scene_cmd = Command(title="Load Scene", callback=load_scene)


def save_scene(viewer: "Viewer"):
    result = QFileDialog.getSaveFileName(parent=viewer.ui.window.widget, filter="JSON files (*.json)")
    if not result:
        return

    compas.json_dump(viewer.scene, result[0])


save_scene_cmd = Command(title="Save Scene", callback=save_scene)


# =============================================================================
# =============================================================================
# =============================================================================
# Data
# =============================================================================
# =============================================================================
# =============================================================================


def load_data():
    pass


load_data_cmd = Command(title="Load Data", callback=lambda: print("load data"))


# =============================================================================
# =============================================================================
# =============================================================================
# Info
# =============================================================================
# =============================================================================
# =============================================================================


def obj_settings(viewer: "Viewer"):
    ObjectSettingDialog().exec()


obj_settings_cmd = Command(title="Object Settings", callback=obj_settings)
