from .action import Action


class ViewTop(Action):
    """Switch to top."""

    def pressed_action(self):
        self.viewer.render.viewmode = "top"


class ViewPerspective(Action):
    """Switch to perspective."""

    def pressed_action(self):
        self.viewer.render.viewmode = "perspective"


class ViewFront(Action):
    """Switch to front."""

    def pressed_action(self):
        self.viewer.render.viewmode = "front"


class ViewRight(Action):
    """Switch to right."""

    def pressed_action(self):
        self.viewer.render.viewmode = "right"
