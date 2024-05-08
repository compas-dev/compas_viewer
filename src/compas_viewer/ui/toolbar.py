from compas_viewer.components.button_factory import ButtonFactory


def test_action() -> None:
    print("test action...")


class ToolBar:
    def __init__(self) -> None:
        self.widget = None

    @property
    def viewer(self):
        from compas_viewer.viewer import Viewer

        return Viewer()

    def setup_tool_bar(self):
        self.widget = self.viewer.ui.window.addToolBar("Tools")
        self.widget.setMovable(False)
        self.widget.setObjectName("Tools")
        self.widget.setHidden(not self.viewer.config.ui.toolbar.show)
        self.widget.addWidget(ButtonFactory("zoom_selected.svg", "zoom", test_action()))
