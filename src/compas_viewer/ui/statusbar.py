from compas_viewer.components.widget_tools import LabelWidget


class SatusBar:
    def __init__(self) -> None:
        self.label = LabelWidget()
        self.widget = None

    @property
    def viewer(self):
        from compas_viewer.viewer import Viewer

        return Viewer()

    def lazy_init(self):
        self.widget = self.viewer.ui.window.statusBar()
        self.widget.setHidden(not self.viewer.config.ui.statusbar.show)
        self.widget.addWidget(self.label(text="Ready..."))
