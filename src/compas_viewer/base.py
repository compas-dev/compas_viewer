from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compas_viewer.scene import ViewerScene
    from compas_viewer.viewer import Viewer


class Base:
    """Provide viewer components with access to the shared viewer and scene."""

    @property
    def viewer(self) -> "Viewer":
        """The shared viewer instance."""
        from compas_viewer.viewer import Viewer

        return Viewer()

    @property
    def scene(self) -> "ViewerScene":
        """The scene owned by the shared viewer."""
        return self.viewer.scene
