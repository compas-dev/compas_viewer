from compas_viewer.base import Base
from compas_viewer.components.widget_tools import LabelWidget


class SatusBar(Base):
    def __init__(self) -> None:
        self.label = LabelWidget()
        self.widget = None

    def setup_status_bar(self):
        self.widget = self.viewer.ui.window.statusBar()
        self.widget.setHidden(not self.viewer.config.ui.statusbar.show)
        self.widget.addWidget(self.label(text="Ready..."))
