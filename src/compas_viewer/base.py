class Base:
    @property
    def viewer(self):
        from compas_viewer.viewer import Viewer

        return Viewer()
