from numpy import float32
from numpy import identity

from OpenGL import GL
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QMouseEvent
from PySide6.QtGui import QWheelEvent

from compas_viewer.base import Base
from compas.colors import Color
from compas_viewer.view3d.camera import Camera
from compas_viewer.components.renderer.shaders import Shader


class BaseOpenGLWidget(QOpenGLWidget, Base):
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
        GL.glViewport(0, 0, 1280, 720)
        # Add rendering code here


class InteractiveOpenGLWidget(BaseOpenGLWidget):
    def __init__(self):
        super().__init__()

        # TODO(pitsai):
        # Controller()
        # Selector()

    def mousePressEvent(self, event: QMouseEvent):
        """
        Callback for the mouse press event which passes the event to the controller.

        Parameters
        ----------
        event : :PySide6:`PySide6/QtGui/QMouseEvent`
            The Qt event.

        See Also
        --------
        :func:`compas_viewer.controller.Controller.mouse_press_action`

        References
        ----------
        * https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html#PySide6.QtWidgets.PySide6.QtWidgets.QWidget.mousePressEvent

        """
        if self.isActiveWindow() and self.underMouse():
            self.viewer.controller.mouse_press_action(event)
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Callback for the release press event which passes the event to the controller.

        Parameters
        ----------
        event : :PySide6:`PySide6/QtGui/QMouseEvent`
            The Qt event.

        See Also
        --------
        :func:`compas_viewer.controller.Controller.mouse_release_action`

        References
        ----------
        * https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html#PySide6.QtWidgets.PySide6.QtWidgets.QWidget.mouseReleaseEvent

        """
        if self.isActiveWindow() and self.underMouse():
            self.viewer.controller.mouse_release_action(event)
            self.update()

    def wheelEvent(self, event: QWheelEvent):
        """
        Callback for the mouse wheel event which passes the event to the controller.

        Parameters
        ----------
        event : :PySide6:`PySide6/QtGui/QWheelEvent`
            The Qt event.

        See Also
        --------
        :func:`compas_viewer.controller.Controller.wheel_action`

        References
        ----------
        * https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html#PySide6.QtWidgets.PySide6.QtWidgets.QWidget.wheelEvent

        """
        if self.isActiveWindow() and self.underMouse():
            self.viewer.controller.wheel_action(event)
            self.update()

    def mouseMoveEvent(self, event):
        # print(f"Mouse moved to {event.position()}")
        pass


class View3D(InteractiveOpenGLWidget):
    def __init__(self):
        super().__init__()

        # TODO(pitsai): config
        self.w = 1280
        self.h = 720
        self.opacity = 0.8
        self.selector_color = Color.yellow()
        self.shader_model = None

        self.camera = Camera()

    def lazy_init(self):
        """
        Paint all the items in the render, which only be called by the paintGL function
        and determines the performance of the renders
        This function introduces decision tree for different render modes and settings.
        It is only  called by the :class:`compas_viewer.components.render.Render.paintGL` function.

        See Also
        --------
        :func:`compas_viewer.components.render.Render.paintGL`
        :func:`compas_viewer.components.render.Render.paint_instance`
        """

        self.camera.lazy_init()

        for obj in self.viewer.scene.objects:
            obj.init()

        # TODO(pitsai): impliment shader
        projection = self.camera.projection(self.w, self.h)
        viewworld = self.camera.viewworld()
        transform = list(identity(4, dtype=float32))

        self.shader_model = Shader(name="model")
        self.shader_model.bind()
        self.shader_model.uniform4x4("projection", projection)
        self.shader_model.uniform4x4("viewworld", viewworld)
        self.shader_model.uniform4x4("transform", transform)
        self.shader_model.uniform1i("is_selected", 0)
        self.shader_model.uniform1f("opacity", self.opacity)
        self.shader_model.uniform3f("selection_color", self.selector_color)
        self.shader_model.release()

        #  Matrix update
        viewworld = self.camera.viewworld()
        self.update_projection()
        # Object categorization
        mesh_objs = self.viewer.scene.sort_objects_from_category("MeshObject")
        # tag_objs, vector_objs, mesh_objs = self.sort_objects_from_category((obj for obj in self.viewer.scene.objects if obj.is_visible))

        # Draw model objects in the scene
        self.shader_model.bind()
        for obj in mesh_objs:
            obj.draw(self.shader_model, True, False)
        self.shader_model.release()

    def paintGL(self):
        self.clear()
        super().paintGL()

    def update_projection(self, w=None, h=None):
        """
        Update the projection matrix.

        Parameters
        ----------
        w : int, optional
            The width of the renderer, by default None.
        h : int, optional
            The height of the renderer, by default None.
        """
        # TODO(pitsai): recalculating is only performed when the viewport size changes.
        projection = self.camera.projection(self.w, self.h)
        self.shader_model.bind()
        self.shader_model.uniform4x4("projection", projection)
        self.shader_model.release()
