from typing import TYPE_CHECKING

from compas_viewer.configurations import ActionConfig

from .action import Action

if TYPE_CHECKING:
    from compas_viewer.viewer import Viewer


class ZoomSelected(Action):
    """Look at action."""

    def __init__(self, name, viewer: "Viewer", config: ActionConfig):
        super().__init__(name, viewer, config)

    def pressed(self):
        raise NotImplementedError
