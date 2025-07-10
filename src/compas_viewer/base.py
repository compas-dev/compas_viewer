class Base:
    """
    Base class for all components in the viewer, provides a global access to the viewer and scene.

    Attributes
    ----------
    viewer : Viewer
        The viewer instance.
    scene : Scene
        The scene instance.
    """

    @property
    def viewer(self):
        from compas_viewer.viewer import Viewer

        return Viewer()

    @property
    def scene(self):
        return self.viewer.scene
