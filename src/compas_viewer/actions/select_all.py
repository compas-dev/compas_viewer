from .action import Action


class SelectAll(Action):
    """Select all objects."""

    def pressed_action(self):
        for obj in self.viewer.objects:
            obj.is_selected = True
        self.viewer.renderer.update()
