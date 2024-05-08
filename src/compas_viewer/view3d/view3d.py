from OpenGL import GL
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from compas_viewer.view3d.camera import Camera


class BaseOpenGLWidget(QOpenGLWidget):
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
        # Add rendering code here


class InteractiveOpenGLWidget(BaseOpenGLWidget):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event):
        print(f"Mouse pressed at {event.position()}")

    def mouseMoveEvent(self, event):
        print(f"Mouse moved to {event.position()}")


class View3D(InteractiveOpenGLWidget):
    def __init__(self):
        super().__init__()

        self.camera = Camera()
        # TODO(pitsai): impliment shader
        # self.shader_model = Shader(name="model")

    def paintGL(self):
        super().paintGL()
        self.renderCustomScene()

    def renderCustomScene(self):
        # Placeholder for custom rendering logic
        pass
