from .action import Action


class ZoomSelected(Action):
    """Look at action."""

    def pressed(self):
        raise NotImplementedError
