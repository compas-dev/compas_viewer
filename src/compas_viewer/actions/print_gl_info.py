from typing import TYPE_CHECKING

from compas_viewer.configurations import ActionConfig
from compas_viewer.utilities import gl_info

from .action import Action

if TYPE_CHECKING:
    from compas_viewer.viewer import Viewer


class GLInfo(Action):
    """
    Pop up a window with OpenGL information.
    """

    def __init__(self, name, viewer: "Viewer", config: ActionConfig):
        super().__init__(name, viewer, config)

    def pressed(self):
        self.viewer.info(gl_info())
