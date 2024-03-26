from compas_viewer.utilities import gl_info

from .action import Action


class CameraInfo(Action):
    """
    Pop up a window with camera information.
    """

    def pressed_action(self):
        self.viewer.renderer.update()
        info = f"""
        Camera position: {self.viewer.renderer.camera.position}
        Camera target: {self.viewer.renderer.camera.target}
        Camera distance: {self.viewer.renderer.camera.distance}
        Camera fov: {self.viewer.renderer.camera.config.fov}
        Camera near: {self.viewer.renderer.camera.config.near}
        Camera far: {self.viewer.renderer.camera.config.far}
        Camera scale : {self.viewer.renderer.camera.config.scale}
        Camera zoomdelta : {self.viewer.renderer.camera.config.zoomdelta}
        Camera rotationdelta : {self.viewer.renderer.camera.config.rotationdelta}
        Camera pan_delta : {self.viewer.renderer.camera.config.pan_delta}
        """
        self.viewer.layout.window.info(info)


class SelectionInfo(Action):
    """
    Pop up a window with selection information.
    """

    def pressed_action(self):
        info = "Selected objects: \n"

        for i, obj in enumerate(self.scene.objects):
            if obj.is_selected:
                info += f"Object {i}: {obj} \n"

        self.viewer.layout.window.info(info)


class GLInfo(Action):
    """
    Pop up a window with OpenGL information.
    """

    def pressed_action(self):
        self.viewer.layout.window.info(gl_info())
