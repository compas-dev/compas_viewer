from compas_viewer.utilities import gl_info

from .action import Action


class GLInfo(Action):
    """
    Pop up a window with OpenGL information.
    """

    def pressed(self):
        self.viewer.info(gl_info())
