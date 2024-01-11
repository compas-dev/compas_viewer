from .action import Action


class SelectAll(Action):
    """Look at action."""

    def pressed_action(self):
        for obj in self.viewer.objects:
            obj.is_selected = True
        self.viewer.renderer.update()
