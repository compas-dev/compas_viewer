from OpenGL import GL
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from compas_viewer.components.default_component_factory import ViewerSetting, ViewerTreeForm

from compas_viewer.components.renderer import Renderer
from compas_viewer.configurations import RendererConfig

class OpenGLWidget(QOpenGLWidget):
    def __init__(self) -> None:
        super().__init__()
        self.initializeGL()

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
    def __init__(self) -> None:
        self.viewmode = "perspective"
        self.renderer = OpenGLWidget()

class SideBarRightDefault:
    pass

class SideBarRight:
    def __init__(self) -> None:

        self.setting = ViewerSetting()
        self.tree_form = ViewerTreeForm(self.viewer.scene)
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.splitter.setChildrenCollapsible(True)
        # self.scenetree = SceneTreeView()
        # self.objectlist = ObjectListView()
        # self.camerasettings = CameraSettings()

        
        # self.splitter.addWidget(self.scenetree.widget)
        # self.splitter.addWidget(self.objectlist.widget)
        
        ### Slot 1
        self.splitter.addWidget(self.tree_form.tree_view())
        ### Slot 2
        self.splitter.addWidget(self.setting.camera_all_setting())
        self.splitter.setHidden(not self.viewer.config.ui.sidebar.show)
        pass
    
    @property
    def viewer(self):
        from compas_viewer.main import Viewer
        return Viewer()


class ViewPort:
    def __init__(self):
        self.view3d = View3D()
        self.sidebar = SideBarRight()

    @property
    def viewer(self):
        from compas_viewer.main import Viewer
        return Viewer()

    def setup_view_port(self):
        self.splitter = QtWidgets.QSplitter()
        self.splitter.addWidget(self.view3d.renderer)
        self.splitter.addWidget(self.sidebar.splitter)
        self.viewer.ui.window.centralWidget().layout().addWidget(self.splitter)
