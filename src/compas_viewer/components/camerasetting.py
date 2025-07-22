from .button import Button
from .container import Container
from .numberedit import NumberEdit


class CameraSetting(Container):
    """
    A form component for displaying and updating camera settings in the viewer.
    This component allows users to modify the camera's target and position
    with real-time updates.

    Attributes
    ----------
    target_x : NumberEdit
        Number editor for camera target X coordinate.
    target_y : NumberEdit
        Number editor for camera target Y coordinate.
    target_z : NumberEdit
        Number editor for camera target Z coordinate.
    position_x : NumberEdit
        Number editor for camera position X coordinate.
    position_y : NumberEdit
        Number editor for camera position Y coordinate.
    position_z : NumberEdit
        Number editor for camera position Z coordinate.
    fov : NumberEdit
        Number editor for camera field of view.
    near : NumberEdit
        Number editor for camera near plane.
    far : NumberEdit
        Number editor for camera far plane.
    scale : NumberEdit
        Number editor for camera scale.
    zoomdelta : NumberEdit
        Number editor for camera zoom delta.
    rotationdelta : NumberEdit
        Number editor for camera rotation delta.
    pandelta : NumberEdit
        Number editor for camera pan delta.
    reset_button : Button
        Button to reset camera to default position.

    Example
    -------
    >>> camera_setting = CameraSetting()
    >>> camera_setting.update()
    """

    def __init__(self) -> None:
        super().__init__(container_type="scrollable")
        self.populate()

    def populate(self) -> None:
        """Populate the form with camera setting components."""
        self.reset()

        if not hasattr(self.viewer, "ui"):
            # If the ui is not initialized, don't populate the form
            return

        def _update_camera(*args):
            self.viewer.renderer.update()

        camera = self.viewer.renderer.camera

        # Create NumberEdit components for target (bind directly to camera.target)
        self.target_x = NumberEdit(camera.target, "x", title="Target X", action=_update_camera)
        self.target_y = NumberEdit(camera.target, "y", title="Target Y", action=_update_camera)
        self.target_z = NumberEdit(camera.target, "z", title="Target Z", action=_update_camera)

        # Create NumberEdit components for position (bind directly to camera.position)
        self.position_x = NumberEdit(camera.position, "x", title="Position X", action=_update_camera)
        self.position_y = NumberEdit(camera.position, "y", title="Position Y", action=_update_camera)
        self.position_z = NumberEdit(camera.position, "z", title="Position Z", action=_update_camera)

        # Create NumberEdit components for camera properties (bind directly to camera)
        self.fov = NumberEdit(camera, "fov", title="Field of View", step=1.0, min_val=1.0, max_val=179.0, action=_update_camera)
        self.near = NumberEdit(camera, "near", title="Near Plane", action=_update_camera)
        self.far = NumberEdit(camera, "far", title="Far Plane", min_val=10.0, max_val=10000.0, action=_update_camera)
        self.scale = NumberEdit(camera, "scale", title="Scale", min_val=0.1, max_val=10.0, action=_update_camera)
        self.zoomdelta = NumberEdit(camera, "zoomdelta", title="Zoom Delta", min_val=0.001, max_val=1.0, action=_update_camera)
        self.rotationdelta = NumberEdit(camera, "rotationdelta", title="Rotation Delta", step=0.01, decimals=2, min_val=0.001, max_val=1.0, action=_update_camera)
        self.pandelta = NumberEdit(camera, "pandelta", title="Pan Delta", min_val=0.001, max_val=1.0, action=_update_camera)

        # Add components to the form
        self.add(self.target_x)
        self.add(self.target_y)
        self.add(self.target_z)
        self.add(self.position_x)
        self.add(self.position_y)
        self.add(self.position_z)
        self.add(self.fov)
        self.add(self.near)
        self.add(self.far)
        self.add(self.scale)
        self.add(self.zoomdelta)
        self.add(self.rotationdelta)
        self.add(self.pandelta)

        # Add reset button
        def _reset_camera():
            """Reset camera to default settings."""
            camera = self.viewer.renderer.camera
            config = self.viewer.config.camera

            # Reset all camera properties to config defaults
            camera.target.set(*config.target)
            camera.position.set(*config.position)
            camera.fov = config.fov
            camera.near = config.near
            camera.far = config.far
            camera.scale = config.scale
            camera.zoomdelta = config.zoomdelta
            camera.rotationdelta = config.rotationdelta
            camera.pandelta = config.pandelta

            self.viewer.renderer.update()
            # Update the form values
            self.update()

        self.reset_button = Button(text="Reset to Defaults", action=_reset_camera)
        self.add(self.reset_button)

    def update(self) -> None:
        """Update the form with current camera settings."""
        self.populate()

        camera = self.viewer.renderer.camera

        # Update the NumberEdit components
        if hasattr(self, "target_x"):
            self.target_x.spinbox.setValue(camera.target.x)
            self.target_y.spinbox.setValue(camera.target.y)
            self.target_z.spinbox.setValue(camera.target.z)

            self.position_x.spinbox.setValue(camera.position.x)
            self.position_y.spinbox.setValue(camera.position.y)
            self.position_z.spinbox.setValue(camera.position.z)

            self.fov.spinbox.setValue(camera.fov)
            self.near.spinbox.setValue(camera.near)
            self.far.spinbox.setValue(camera.far)
            self.scale.spinbox.setValue(camera.scale)
            self.zoomdelta.spinbox.setValue(camera.zoomdelta)
            self.rotationdelta.spinbox.setValue(camera.rotationdelta)
            self.pandelta.spinbox.setValue(camera.pandelta)
