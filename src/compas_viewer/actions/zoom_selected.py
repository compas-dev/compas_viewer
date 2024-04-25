from numpy import array
from numpy.linalg import norm

from .action import Action


class ZoomSelected(Action):
    """Look at action."""

    def pressed_action(self):
        selected_objs = [obj for obj in self.scene.objects if obj.is_selected]
        self.viewer.renderer.camera.zoom_extents(selected_objs)
        self.viewer.renderer.update()
