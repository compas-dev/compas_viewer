from compas_viewer.components import CameraSettingsDialog


def a():
    print("action a")


def b():
    print("action b")


def open_camera_settings_dialog():
    dialog = CameraSettingsDialog()
    dialog.exec()


def change_viewmode(mode: str, *args, **kwargs):
    from compas_viewer import Viewer

    viewer = Viewer()
    viewer.renderer.viewmode = mode.lower()
    viewer.renderer.update()
