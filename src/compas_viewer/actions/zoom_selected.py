from numpy import array
from numpy.linalg import norm

from .action import Action


class ZoomSelected(Action):
    """Look at action."""

    def pressed_action(self):
        selected_objs = [obj for obj in self.viewer.objects if obj.is_selected]
        if len(selected_objs) == 0:
            selected_objs = self.viewer.objects
        extents = []

        for obj in selected_objs:
            if obj.bounding_box is not None:
                extents.append(obj.bounding_box)

        extents = array([obj.bounding_box for obj in selected_objs if obj.bounding_box is not None])

        if len(extents) == 0:
            return

        extents = extents.reshape(-1, 3)
        max_corner = extents.max(axis=0)
        min_corner = extents.min(axis=0)
        center = (max_corner + min_corner) / 2
        distance = max(norm(max_corner - min_corner), 1)

        self.viewer.renderer.camera.target = center
        vec = (self.viewer.renderer.camera.target - self.viewer.renderer.camera.position) / norm(
            self.viewer.renderer.camera.target - self.viewer.renderer.camera.position
        )
        self.viewer.renderer.camera.position = self.viewer.renderer.camera.target - vec * distance * 1.5
        self.viewer.renderer.update()
