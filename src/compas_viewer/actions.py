from typing import TYPE_CHECKING

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

from compas_viewer.components import CameraSettingsDialog

if TYPE_CHECKING:
    from compas_viewer import Viewer


def clear_scene():
    from compas_viewer import Viewer

    viewer = Viewer()

    for obj in viewer.scene.objects:
        viewer.scene.remove(obj)
        del obj

    viewer.renderer.update()


def delete_selected():
    from compas_viewer import Viewer

    viewer = Viewer()

    for obj in viewer.scene.objects:
        if obj.is_selected:
            viewer.scene.remove(obj)
            del obj
    viewer.renderer.update()


def open_camera_settings_dialog():
    dialog = CameraSettingsDialog()
    dialog.exec()


def change_viewmode(mode: str, *args, **kwargs):
    from compas_viewer import Viewer

    viewer = Viewer()
    viewer.renderer.viewmode = mode.lower()
    viewer.renderer.update()


def zoom_selected():
    from compas_viewer import Viewer

    viewer = Viewer()

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


def select_all():
    from compas_viewer import Viewer

    viewer = Viewer()

    for obj in viewer.scene.objects:
        if obj.show and not obj.is_locked:
            obj.is_selected = True

    viewer.renderer.update()


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


def zoom_view(viewer: "Viewer", event: QWheelEvent):
    degrees = event.angleDelta().y() / 8
    steps = degrees / 15
    viewer.renderer.camera.zoom(steps)
    viewer.renderer.update()


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

        # Select base don instance colors
        for color, obj in viewer.scene.instance_colors.items():
            if any(all(color == unique_colors, axis=1)):
                obj.is_selected = True
                continue

    viewer.ui.sidebar.update()
    viewer.renderer.update()


def deselect_window():
    pass
