from PySide6 import QtCore
from PySide6 import QtWidgets

from compas_viewer.view3d.view3d import View3D


class SideBarRight:
    def __init__(self) -> None:
        super().__init__()
        self.side_right_widget = None
        self.default_widgets: list[str] = ["TreeForm"]
        self.custom_widgets: list[str] = []  # TODO(pitsai): self.viewer.config.ui.sidebar.items
        self.widget_list: list = self.default_widgets + self.custom_widgets

    @property
    def viewer(self):
        from compas_viewer.viewer import Viewer

        return Viewer()

    def setup_sidebar_right(self) -> None:
        self.side_right_widget = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.side_right_widget.setChildrenCollapsible(True)
        self.viewer.ui.components_manager.add_widgets(self.widget_list)
        self.side_right_widget = self.viewer.ui.components_manager.setup_widgets(self.side_right_widget)
        self.side_right_widget.setHidden(not self.viewer.config.ui.sidebar.show)


class ViewPort:
    def __init__(self):
        self.sidebar_right = SideBarRight()

    @property
    def viewer(self):
        from compas_viewer.viewer import Viewer

        return Viewer()

    def setup_view_port(self) -> None:
        self.sidebar_right.setup_sidebar_right()

        self.viewport_widget = QtWidgets.QSplitter()
        self.viewport_widget.addWidget(View3D())
        self.viewport_widget.addWidget(self.sidebar_right.side_right_widget)
        self.viewer.ui.window.centralWidget().layout().addWidget(self.viewport_widget)
