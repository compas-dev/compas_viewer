from compas_viewer.base import Base
from compas_viewer.components.button import Button


def test_action() -> None:
    pass


class ToolBar(Base):
    def __init__(self) -> None:
        self.widget = None

    def lazy_init(self):
        self.widget = self.viewer.ui.window.addToolBar("Tools")
        self.widget.setMovable(False)
        self.widget.setObjectName("Tools")
        self.widget.setHidden(not self.viewer.config.ui.toolbar.show)
        self.widget.addWidget(Button("zoom_selected.svg", "zoom", test_action()))
