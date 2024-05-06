from PySide6 import QtWidgets
from PySide6.QtCore import Qt

from compas_viewer.layout import Treeform

from .box_factory import BoxFactory


class ViewerSetting:
    def __init__(self) -> None:
        self.box_factory=BoxFactory()

    def camera_target_setting(self) -> QtWidgets.QGroupBox:
        widget = QtWidgets.QGroupBox()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.box_factory.double_edit_widget("X", 0, 0, 100000))
        layout.addWidget(self.box_factory.double_edit_widget("Y", 0, 0, 100000))
        layout.addWidget(self.box_factory.double_edit_widget("Z", 0, 0, 100000))
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)
        widget.setTitle("Camera target")
        widget.setLayout(layout)
        return widget 
    
    def camera_location_setting(self) -> QtWidgets.QGroupBox:
        widget = QtWidgets.QGroupBox()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.box_factory.double_edit_widget("X", 0, 0, 100000))
        layout.addWidget(self.box_factory.double_edit_widget("Y", 0, 0, 100000))
        layout.addWidget(self.box_factory.double_edit_widget("Z", 0, 0, 100000))
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)
        widget.setTitle("Camera location")
        widget.setLayout(layout)
        return widget 

    def camera_pov_setting(self) -> QtWidgets.QGroupBox:
        widget = QtWidgets.QGroupBox()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.box_factory.double_edit_widget("FOV", 50, 10, 80))
        layout.addWidget(self.box_factory.double_edit_widget("NEAR", 0.1, 0.001, 1000))
        layout.addWidget(self.box_factory.double_edit_widget("FAR", 1000, 1, 10000000))
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)
        widget.setTitle("Camera pov")
        widget.setLayout(layout)
        return widget 
    
    def camera_all_setting(self) -> QtWidgets.QVBoxLayout:
        layout = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QFrame()
        widget.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        widget.setLayout(layout)
        layout.addWidget(self.camera_target_setting())
        layout.addWidget(self.camera_location_setting())
        layout.addWidget(self.camera_pov_setting())
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addStretch()
        return widget

class ViewerTreeForm:
    
    @property
    def viewer(self):
        from compas_viewer.main import Viewer
        return Viewer()

    def tree_view(self) -> QtWidgets.QSplitter:
        form_ids = Treeform(self.viewer.scene, {"Name": (lambda o: o.name), "Object": (lambda o: o)})
        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.addWidget(form_ids)
        return splitter

