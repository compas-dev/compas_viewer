from .action import Action


class SelectAll(Action):
    """Select all objects."""

    def pressed_action(self):
        for obj in self.viewer.scene.objects:
            if obj.show and not obj.is_locked:
                obj.is_selected = True
        self.viewer.renderer.update()
