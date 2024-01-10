from typing import TYPE_CHECKING

from compas_viewer.configurations import ActionConfig

from .action import Action

if TYPE_CHECKING:
    from compas_viewer.viewer import Viewer


class ImportFile(Action):
    """Import a file into the viewer."""

    def pressed_action(self):
        print("Importing file")


class ExportFile(Action):
    """Export a file from the viewer."""

    def pressed_action(self):
        print("Exporting file")


class OpenURL(Action):
    """Open external url."""

    def __init__(self, name: str, viewer: "Viewer", config: ActionConfig, url: str):
        super().__init__(name, viewer, config)
        self.url = url

    def pressed_action(self):
        print(f"Linking url: {self.url}.")
