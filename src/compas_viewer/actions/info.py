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
        Camera fov: {self.viewer.config.camera.fov}
        Camera near: {self.viewer.config.camera.near}
        Camera far: {self.viewer.config.camera.far}
        Camera scale : {self.viewer.config.camera.scale}
        Camera zoomdelta : {self.viewer.config.camera.zoomdelta}
        Camera rotationdelta : {self.viewer.config.camera.rotationdelta}
        Camera pan_delta : {self.viewer.config.camera.pan_delta}
        """
        self.viewer.layout.window.info(info)


class SelectionInfo(Action):
    """
    Pop up a window with selection information.
    """

    def pressed_action(self):
        info = "Selected objects: \n"

        for i, obj in enumerate(self.viewer.scene.objects):
            if obj.is_selected:
                info += f"Object {i}: {obj} \n"

        raise NotImplementedError


class GLInfo(Action):
    """
    Pop up a window with OpenGL information.
    """

    def pressed_action(self):
        raise NotImplementedError
