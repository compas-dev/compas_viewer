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
