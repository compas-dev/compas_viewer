from OpenGL import GL
from PySide6 import QtCore
from PySide6 import QtWidgets
from compas_viewer.components.component_manager import ComponentsManager

class SideBarRight(ComponentsManager):
    def __init__(self) -> None:
        super().__init__()
        self.default_widgets: list[dict[str, str]] = [{"type": "tree_view", "temp": "temp"}]
        self.custom_widgets: list[dict[str, str]] = [] #TODO(pitsai): self.viewer.config.ui.sidebar.items
        self.all_widgets: list = self.default_widgets + self.custom_widgets 
        # TODO(pitsai): check nameings
        self.side_right_widget = None

    @property
    def viewer(self):
        from compas_viewer.main import Viewer
        return Viewer()
    
    def setup_sidebar_right(self) -> None:
        self.side_right_widget = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.side_right_widget.setChildrenCollapsible(True)
        self.add_widgets(self.all_widgets)
        self.side_right_widget = self.setup_widgets(self.side_right_widget)
        self.side_right_widget.setHidden(not self.viewer.config.ui.sidebar.show)

class ViewPort:
    def __init__(self):
        self.sidebar_right = SideBarRight()

    @property
    def viewer(self):
        from compas_viewer.main import Viewer
        return Viewer()

    def setup_view_port(self) -> None:
        self.sidebar_right.setup_sidebar_right()

        self.viewport_widget = QtWidgets.QSplitter()
        self.viewport_widget.addWidget(self.viewer.renderer)
        self.viewport_widget.addWidget(self.sidebar_right.side_right_widget)
        self.viewer.ui.window.centralWidget().layout().addWidget(self.viewport_widget)
