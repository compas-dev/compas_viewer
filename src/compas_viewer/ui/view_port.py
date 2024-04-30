from OpenGL import GL
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from compas_viewer.components.component_manager import ComponentsManager

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
        self.view3d = View3D()
        self.sidebar_right = SideBarRight()

    @property
    def viewer(self):
        from compas_viewer.main import Viewer
        return Viewer()

    def setup_view_port(self) -> None:
        self.sidebar_right.setup_sidebar_right()

        self.viewport_widget = QtWidgets.QSplitter()
        self.viewport_widget.addWidget(self.view3d.renderer)
        self.viewport_widget.addWidget(self.sidebar_right.side_right_widget)
        self.viewer.ui.window.centralWidget().layout().addWidget(self.viewport_widget)
