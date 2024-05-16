from .action import Action


class DeleteSelected(Action):
    """Permanently delete selected objects from the viewer and release the memory."""

    def pressed_action(self):
        for obj in self.viewer.scene.objects:
            if obj.is_selected:
                self.viewer.scene.remove(obj)
                del obj
        self.viewer.renderer.update()
