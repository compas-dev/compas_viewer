from numpy import array
from numpy.linalg import norm

from compas_viewer.components import CameraSettingsDialog


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
