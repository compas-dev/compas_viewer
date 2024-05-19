from PySide6 import QtCore
from PySide6 import QtWidgets

from compas_viewer.base import Base
from compas_viewer.components.treeform import Treeform
from compas_viewer.view3d.view3d import View3D


class SideBarRight(Base):
    def __init__(self) -> None:
        super().__init__()
        self.side_right_widget = None

    def lazy_init(self) -> None:
        self.side_right_widget = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.side_right_widget.setChildrenCollapsible(True)
        self.side_right_widget.addWidget(Treeform(self.viewer.scene, {"Name": (lambda o: o.name), "Object": (lambda o: o)}))
        self.side_right_widget.setSizes([800, 200])
        self.side_right_widget.setHidden(not self.viewer.config.ui.sidebar.show)


class ViewPort(Base):
    def __init__(self):
        self.sidebar_right = SideBarRight()

    def lazy_init(self) -> None:
        self.sidebar_right.lazy_init()

        self.viewport_widget = QtWidgets.QSplitter()
        self.viewport_widget.addWidget(self.viewer.view3d)
        self.viewport_widget.addWidget(self.sidebar_right.side_right_widget)
        self.viewport_widget.setSizes([800, 200])
        self.viewer.ui.window.centralWidget().layout().addWidget(self.viewport_widget)
