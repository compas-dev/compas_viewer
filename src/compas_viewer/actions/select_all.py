from .action import Action


class SelectAll(Action):
    """Select all objects."""

    def pressed_action(self):
        for obj in self.scene.objects:
            if obj.is_visible and not obj.is_locked:
                obj.is_selected = True
        self.viewer.renderer.update()
