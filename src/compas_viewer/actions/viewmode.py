from .action import Action


class ViewTop(Action):
    """Switch to top."""

    def pressed_action(self):
        self.viewer.renderer.viewmode = "top"


class ViewPerspective(Action):
    """Switch to perspective."""

    def pressed_action(self):
        self.viewer.renderer.viewmode = "perspective"


class ViewFront(Action):
    """Switch to front."""

    def pressed_action(self):
        self.viewer.renderer.viewmode = "front"


class ViewRight(Action):
    """Switch to right."""

    def pressed_action(self):
        self.viewer.renderer.viewmode = "right"
