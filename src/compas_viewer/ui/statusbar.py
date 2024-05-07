from compas_viewer.components.widget_tools import LabelWidget


class SatusBar:
    def __init__(self) -> None:
        self.label = LabelWidget()
        self.widget = None

    @property
    def viewer(self):
        from compas_viewer.main import Viewer

        return Viewer()

    def setup_status_bar(self):
        self.widget = self.viewer.ui.window.statusBar()
        self.widget.setHidden(not self.viewer.config.ui.statusbar.show)
        self.widget.addWidget(self.label(text="Ready..."))
