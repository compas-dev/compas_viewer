from typing import TYPE_CHECKING
from OpenGL import GL
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6.QtOpenGLWidgets import QOpenGLWidget

if TYPE_CHECKING:
    from .ui import UI

class OpenGLWidget(QOpenGLWidget):
    def __init__(self) -> None:
        super().__init__()

    def clear(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore

    def initializeGL(self):
        GL.glClearColor(0.7, 0.7, 0.7, 1.0)
        GL.glPolygonOffset(1.0, 1.0)
        GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glEnable(GL.GL_POINT_SMOOTH)
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glEnable(GL.GL_FRAMEBUFFER_SRGB)

    def resizeGL(self, w: int, h: int):
        GL.glViewport(0, 0, w, h)


class View3D:
    def __init__(self, viewport: "ViewPort") -> None:
        self.viewport = viewport
        self.viewmode = "perspective"
        self.renderer = OpenGLWidget()

class SideBarRight:
    def __init__(self, viewport: "ViewPort") -> None:
        self.viewport = viewport
        # self.scenetree = SceneTreeView()
        # self.objectlist = ObjectListView()
        # self.camerasettings = CameraSettings()

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.splitter.setChildrenCollapsible(True)
        # self.splitter.addWidget(self.scenetree.widget)
        # self.splitter.addWidget(self.objectlist.widget)
        # self.splitter.addWidget(self.camerasettings.widget)

class ViewPort:
    def __init__(self, ui: "UI"):
        self.ui = ui
        self.view3d = View3D(self)
        self.sidebar = SideBarRight(self)
        self.splitter = QtWidgets.QSplitter()
        self.splitter.addWidget(self.view3d.renderer)
        self.splitter.addWidget(self.sidebar.splitter)

class CameraSettings:
    def __init__(self) -> None:
        self.layout = QtWidgets.QVBoxLayout()
        self.widget = QtWidgets.QFrame()
        self.widget.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.widget.setLayout(self.layout)

        fov = DoubleSpinnerWidget("FOV", 50, 10, 80)
        near = DoubleSpinnerWidget("NEAR", 0.1, 0.001, 1000)
        far = DoubleSpinnerWidget("FAR", 1000, 1, 10000000)
        target = CameraTargetWidget()
        location = CameraLocationWidget()

        self.layout.addWidget(target.widget)
        self.layout.addWidget(location.widget)
        self.layout.addWidget(fov.widget)
        self.layout.addWidget(near.widget)
        self.layout.addWidget(far.widget)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.addStretch()