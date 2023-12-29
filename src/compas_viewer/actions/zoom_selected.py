from .action import Action


class ZoomSelected(Action):
    """Look at action."""

    def pressed_action(self):
        raise NotImplementedError
