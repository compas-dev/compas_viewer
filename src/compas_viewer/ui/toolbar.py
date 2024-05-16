from compas_viewer.base import Base
from compas_viewer.components.combobox import ViewModeAction


class ToolBar(Base):
    def __init__(self) -> None:
        self.widget = None

    def lazy_init(self):
        self.widget = self.viewer.ui.window.addToolBar("Tools")
        self.widget.setMovable(False)
        self.widget.setObjectName("Tools")
        self.widget.setHidden(not self.viewer.config.ui.toolbar.show)
        self.widget.addWidget(ViewModeAction().combobox())
